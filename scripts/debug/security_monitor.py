#!/usr/bin/env python3
"""
Security Monitoring Script
Monitors logs for suspicious activities and potential attacks.
"""

import re
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import os
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityMonitor:
    def __init__(self):
        self.suspicious_patterns = {
            'sql_injection': [
                r"(\b(union|select|insert|update|delete|drop|create|alter)\b.*\b(from|into|where|table|database)\b)",
                r"(\b(union|select|insert|update|delete|drop|create|alter)\b.*['\"])",
                r"(\b(union|select|insert|update|delete|drop|create|alter)\b.*\b(admin|user|password|login)\b)",
            ],
            'xss_attempt': [
                r"<script[^>]*>.*</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"<img[^>]*on\w+\s*=",
            ],
            'path_traversal': [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e%5c",
            ],
            'command_injection': [
                r"(\b(cat|ls|pwd|whoami|id|uname|ps|netstat|ifconfig|ipconfig)\b)",
                r"(\b(rm|del|mkdir|touch|chmod|chown)\b)",
                r"(\b(wget|curl|nc|telnet|ssh|ftp)\b)",
            ],
            'rate_limit_violation': [
                r"rate limit exceeded",
                r"too many requests",
            ],
            'failed_auth': [
                r"failed login attempt",
                r"incorrect email or password",
                r"invalid credentials",
            ],
            'suspicious_user_agent': [
                r"(bot|crawler|spider|scraper)",
                r"(sqlmap|nikto|nmap|burp)",
                r"(curl|wget|python-requests)",
            ]
        }
        
        self.thresholds = {
            'failed_logins_per_ip': 5,  # per hour
            'rate_limit_violations_per_ip': 10,  # per hour
            'suspicious_requests_per_ip': 20,  # per hour
            'unique_ips_per_minute': 50,  # for DDoS detection
        }
        
        self.alert_recipients = os.getenv('SECURITY_ALERT_EMAIL', '').split(',')
        
    def parse_log_line(self, line):
        """Parse a log line and extract relevant information"""
        try:
            # Nginx access log format
            # $remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"
            
            # Extract IP address
            ip_match = re.match(r'^(\S+)', line)
            if not ip_match:
                return None
            
            ip = ip_match.group(1)
            
            # Extract timestamp
            time_match = re.search(r'\[([^\]]+)\]', line)
            timestamp = None
            if time_match:
                try:
                    timestamp = datetime.strptime(time_match.group(1), '%d/%b/%Y:%H:%M:%S %z')
                except:
                    timestamp = datetime.now()
            
            # Extract request
            request_match = re.search(r'"([^"]+)"', line)
            request = request_match.group(1) if request_match else ""
            
            # Extract status code
            status_match = re.search(r'"\s+(\d{3})\s+', line)
            status = int(status_match.group(1)) if status_match else 0
            
            # Extract user agent
            ua_match = re.search(r'"([^"]*)"\s*$', line)
            user_agent = ua_match.group(1) if ua_match else ""
            
            return {
                'ip': ip,
                'timestamp': timestamp,
                'request': request,
                'status': status,
                'user_agent': user_agent,
                'raw_line': line
            }
            
        except Exception as e:
            logger.error(f"Error parsing log line: {e}")
            return None
    
    def check_suspicious_patterns(self, log_entry):
        """Check if log entry matches suspicious patterns"""
        if not log_entry:
            return []
        
        suspicious_activities = []
        
        # Check request patterns
        request = log_entry.get('request', '')
        user_agent = log_entry.get('user_agent', '')
        
        for pattern_type, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, request, re.IGNORECASE) or re.search(pattern, user_agent, re.IGNORECASE):
                    suspicious_activities.append({
                        'type': pattern_type,
                        'pattern': pattern,
                        'matched_text': request if re.search(pattern, request, re.IGNORECASE) else user_agent
                    })
        
        return suspicious_activities
    
    def analyze_logs(self, log_file_path, hours_back=1):
        """Analyze logs for security threats"""
        try:
            if not os.path.exists(log_file_path):
                logger.error(f"Log file not found: {log_file_path}")
                return {}
            
            # Calculate time threshold
            threshold_time = datetime.now() - timedelta(hours=hours_back)
            
            # Statistics
            stats = {
                'total_requests': 0,
                'unique_ips': set(),
                'failed_requests': 0,
                'suspicious_activities': [],
                'ip_activity': defaultdict(list),
                'failed_logins': defaultdict(int),
                'rate_limit_violations': defaultdict(int),
                'status_codes': Counter(),
                'user_agents': Counter(),
            }
            
            with open(log_file_path, 'r') as f:
                for line in f:
                    log_entry = self.parse_log_line(line.strip())
                    if not log_entry:
                        continue
                    
                    # Check time threshold
                    if log_entry['timestamp'] and log_entry['timestamp'] < threshold_time:
                        continue
                    
                    stats['total_requests'] += 1
                    stats['unique_ips'].add(log_entry['ip'])
                    stats['ip_activity'][log_entry['ip']].append(log_entry)
                    stats['status_codes'][log_entry['status']] += 1
                    stats['user_agents'][log_entry['user_agent']] += 1
                    
                    # Check for failed requests
                    if log_entry['status'] >= 400:
                        stats['failed_requests'] += 1
                    
                    # Check for suspicious patterns
                    suspicious = self.check_suspicious_patterns(log_entry)
                    if suspicious:
                        stats['suspicious_activities'].append({
                            'log_entry': log_entry,
                            'suspicious_patterns': suspicious
                        })
                    
                    # Check for failed auth attempts
                    if log_entry['status'] == 401 or log_entry['status'] == 403:
                        stats['failed_logins'][log_entry['ip']] += 1
                    
                    # Check for rate limit violations
                    if log_entry['status'] == 429:
                        stats['rate_limit_violations'][log_entry['ip']] += 1
            
            # Convert set to list for JSON serialization
            stats['unique_ips'] = list(stats['unique_ips'])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error analyzing logs: {e}")
            return {}
    
    def detect_threats(self, stats):
        """Detect potential security threats based on statistics"""
        threats = []
        
        # Check for excessive failed logins
        for ip, count in stats['failed_logins'].items():
            if count >= self.thresholds['failed_logins_per_ip']:
                threats.append({
                    'type': 'brute_force_attempt',
                    'ip': ip,
                    'count': count,
                    'threshold': self.thresholds['failed_logins_per_ip'],
                    'severity': 'high'
                })
        
        # Check for rate limit violations
        for ip, count in stats['rate_limit_violations'].items():
            if count >= self.thresholds['rate_limit_violations_per_ip']:
                threats.append({
                    'type': 'rate_limit_abuse',
                    'ip': ip,
                    'count': count,
                    'threshold': self.thresholds['rate_limit_violations_per_ip'],
                    'severity': 'medium'
                })
        
        # Check for suspicious activities
        suspicious_ips = defaultdict(int)
        for activity in stats['suspicious_activities']:
            ip = activity['log_entry']['ip']
            suspicious_ips[ip] += 1
        
        for ip, count in suspicious_ips.items():
            if count >= self.thresholds['suspicious_requests_per_ip']:
                threats.append({
                    'type': 'suspicious_activity',
                    'ip': ip,
                    'count': count,
                    'threshold': self.thresholds['suspicious_requests_per_ip'],
                    'severity': 'medium'
                })
        
        # Check for potential DDoS
        if len(stats['unique_ips']) > self.thresholds['unique_ips_per_minute']:
            threats.append({
                'type': 'potential_ddos',
                'unique_ips': len(stats['unique_ips']),
                'threshold': self.thresholds['unique_ips_per_minute'],
                'severity': 'high'
            })
        
        return threats
    
    def send_alert(self, threats, stats):
        """Send security alert email"""
        if not self.alert_recipients or not threats:
            return
        
        try:
            # Create email content
            subject = f"Security Alert - {len(threats)} threats detected"
            
            body = f"""
Security Alert Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Total requests: {stats.get('total_requests', 0)}
- Unique IPs: {len(stats.get('unique_ips', []))}
- Failed requests: {stats.get('failed_requests', 0)}
- Threats detected: {len(threats)}

Threats:
"""
            
            for threat in threats:
                body += f"""
- Type: {threat['type']}
  IP: {threat.get('ip', 'N/A')}
  Count: {threat.get('count', 'N/A')}
  Severity: {threat['severity']}
"""
            
            # Send email (implement your email sending logic here)
            logger.info(f"Security alert would be sent to: {self.alert_recipients}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Body: {body}")
            
        except Exception as e:
            logger.error(f"Error sending security alert: {e}")
    
    def generate_report(self, log_file_path, hours_back=1):
        """Generate comprehensive security report"""
        logger.info(f"Analyzing logs from {log_file_path} for the last {hours_back} hours")
        
        # Analyze logs
        stats = self.analyze_logs(log_file_path, hours_back)
        
        if not stats:
            logger.error("No log data to analyze")
            return
        
        # Detect threats
        threats = self.detect_threats(stats)
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'analysis_period_hours': hours_back,
            'summary': {
                'total_requests': stats['total_requests'],
                'unique_ips': len(stats['unique_ips']),
                'failed_requests': stats['failed_requests'],
                'threats_detected': len(threats),
                'suspicious_activities': len(stats['suspicious_activities'])
            },
            'threats': threats,
            'top_ips': dict(Counter([entry['ip'] for entries in stats['ip_activity'].values() for entry in entries]).most_common(10)),
            'status_codes': dict(stats['status_codes']),
            'suspicious_activities': stats['suspicious_activities'][:10]  # Top 10
        }
        
        # Send alert if threats detected
        if threats:
            self.send_alert(threats, stats)
        
        return report

def main():
    """Main function"""
    monitor = SecurityMonitor()
    
    # Analyze nginx access logs
    log_files = [
        '/var/log/nginx/access.log',
        './nginx_access.log',  # For testing
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            report = monitor.generate_report(log_file, hours_back=1)
            if report:
                print("=== Security Report ===")
                print(json.dumps(report, indent=2, default=str))
                break
    else:
        print("No log files found to analyze")

if __name__ == "__main__":
    main() 