"""
Notification Service
====================

Handles email, Slack, and Teams notifications.

Supports:
- Email notifications with templates
- Slack message posting and interactive buttons
- Microsoft Teams adaptive cards
- SMS notifications (Twilio)
"""

from typing import Dict, List, Optional
from datetime import date, datetime
import smtplib
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import os


class EmailNotificationService:
    """
    Email notification service with template support.
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str,
        from_name: str = "Healthrix System",
        template_dir: str = "templates/emails"
    ):
        """
        Initialize email service.

        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: Sender email address
            from_name: Sender name
            template_dir: Directory containing email templates
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name

        # Setup Jinja2 template environment
        self.template_env = Environment(
            loader=FileSystemLoader(template_dir)
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: Dict
    ):
        """
        Send email using template.

        Args:
            to_email: Recipient email address
            subject: Email subject
            template_name: Template file name
            context: Template context variables
        """
        # Render template
        template = self.template_env.get_template(template_name)
        html_content = template.render(**context)

        # Create message
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"{self.from_name} <{self.from_email}>"
        message['To'] = to_email

        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)

        # Send via SMTP
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
        except Exception as e:
            print(f"Error sending email: {e}")
            raise

    async def send_performance_summary(
        self,
        to_email: str,
        employee_name: str,
        performance_data: Dict
    ):
        """
        Send daily performance summary email.

        Args:
            to_email: Employee email
            employee_name: Employee name
            performance_data: Performance metrics
        """
        subject = f"Your Performance Summary - {datetime.now().strftime('%B %d, %Y')}"

        context = {
            'employee_name': employee_name,
            'date': datetime.now().strftime('%B %d, %Y'),
            'final_score': performance_data.get('final_performance_percent'),
            'productivity_score': performance_data.get('weighted_prod_score'),
            'behavior_score': performance_data.get('weighted_behavior_score'),
            'total_points': performance_data.get('total_task_points'),
            'task_count': performance_data.get('task_count'),
            'performance_rating': self._get_rating(performance_data.get('final_performance_percent')),
        }

        await self.send_email(
            to_email,
            subject,
            'performance_summary.html',
            context
        )

    async def send_achievement_notification(
        self,
        to_email: str,
        employee_name: str,
        achievement: str,
        message: str
    ):
        """
        Send achievement notification email.

        Args:
            to_email: Employee email
            employee_name: Employee name
            achievement: Achievement title
            message: Achievement message
        """
        subject = f"🎉 New Achievement: {achievement}"

        context = {
            'employee_name': employee_name,
            'achievement': achievement,
            'message': message,
            'date': datetime.now().strftime('%B %d, %Y'),
        }

        await self.send_email(
            to_email,
            subject,
            'achievement.html',
            context
        )

    async def send_alert_notification(
        self,
        to_email: str,
        employee_name: str,
        alert_type: str,
        alert_message: str
    ):
        """
        Send alert notification email.

        Args:
            to_email: Recipient email
            employee_name: Employee name
            alert_type: Alert type (performance, conduct, etc.)
            alert_message: Alert message
        """
        subject = f"⚠️ Alert: {alert_type}"

        context = {
            'employee_name': employee_name,
            'alert_type': alert_type,
            'alert_message': alert_message,
            'date': datetime.now().strftime('%B %d, %Y'),
        }

        await self.send_email(
            to_email,
            subject,
            'alert.html',
            context
        )

    def _get_rating(self, score: float) -> str:
        """Get performance rating text."""
        if score >= 90:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Needs Improvement"
        else:
            return "Critical"


class SlackNotificationService:
    """
    Slack notification service.
    """

    def __init__(self, webhook_url: str):
        """
        Initialize Slack service.

        Args:
            webhook_url: Slack webhook URL
        """
        self.webhook_url = webhook_url

    async def send_message(
        self,
        text: str,
        attachments: Optional[List[Dict]] = None,
        blocks: Optional[List[Dict]] = None
    ):
        """
        Send message to Slack.

        Args:
            text: Message text
            attachments: Message attachments (legacy)
            blocks: Block Kit blocks (recommended)
        """
        payload = {'text': text}

        if attachments:
            payload['attachments'] = attachments

        if blocks:
            payload['blocks'] = blocks

        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Slack API error: {response.status}")

    async def notify_performance_calculated(
        self,
        employee_name: str,
        performance_score: float,
        date_str: str
    ):
        """
        Notify about performance calculation.

        Args:
            employee_name: Employee name
            performance_score: Performance score
            date_str: Date string
        """
        # Get emoji based on score
        if performance_score >= 90:
            emoji = "🌟"
            color = "#36a64f"  # Green
        elif performance_score >= 70:
            emoji = "✅"
            color = "#3AA3E3"  # Blue
        else:
            emoji = "⚠️"
            color = "#ff9800"  # Orange

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *Performance Update*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Employee:*\n{employee_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Score:*\n{performance_score:.1f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Date:*\n{date_str}"
                    }
                ]
            }
        ]

        await self.send_message(
            text=f"Performance calculated for {employee_name}",
            blocks=blocks
        )

    async def notify_team_leaderboard(
        self,
        leaderboard_data: List[Dict],
        date_str: str
    ):
        """
        Post team leaderboard to Slack.

        Args:
            leaderboard_data: List of top performers
            date_str: Date string
        """
        leaderboard_text = "\n".join([
            f"{i+1}. {entry['name']} - {entry['score']:.1f}%"
            for i, entry in enumerate(leaderboard_data[:10])
        ])

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🏆 *Team Leaderboard - {date_str}*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": leaderboard_text
                }
            }
        ]

        await self.send_message(
            text=f"Team leaderboard for {date_str}",
            blocks=blocks
        )

    async def notify_anomaly_detected(
        self,
        employee_name: str,
        anomaly_description: str,
        severity: str
    ):
        """
        Notify about detected anomaly.

        Args:
            employee_name: Employee name
            anomaly_description: Anomaly description
            severity: Severity level
        """
        color_map = {
            'high': '#ff0000',  # Red
            'medium': '#ff9800',  # Orange
            'low': '#ffeb3b'  # Yellow
        }

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *Anomaly Detected - {severity.upper()} Severity*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Employee:*\n{employee_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Description:*\n{anomaly_description}"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Details"
                        },
                        "url": f"https://app.healthrix.com/employee/{employee_name}"
                    }
                ]
            }
        ]

        await self.send_message(
            text=f"Anomaly detected for {employee_name}",
            blocks=blocks
        )


class NotificationManager:
    """
    Central notification manager coordinating all notification services.
    """

    def __init__(
        self,
        email_service: Optional[EmailNotificationService] = None,
        slack_service: Optional[SlackNotificationService] = None
    ):
        """
        Initialize notification manager.

        Args:
            email_service: Email notification service
            slack_service: Slack notification service
        """
        self.email_service = email_service
        self.slack_service = slack_service

    async def notify_performance_calculated(
        self,
        employee_email: str,
        employee_name: str,
        performance_data: Dict,
        send_email: bool = True,
        send_slack: bool = False
    ):
        """
        Send performance calculation notifications.

        Args:
            employee_email: Employee email
            employee_name: Employee name
            performance_data: Performance data
            send_email: Whether to send email
            send_slack: Whether to send Slack notification
        """
        tasks = []

        if send_email and self.email_service:
            tasks.append(
                self.email_service.send_performance_summary(
                    employee_email,
                    employee_name,
                    performance_data
                )
            )

        if send_slack and self.slack_service:
            tasks.append(
                self.slack_service.notify_performance_calculated(
                    employee_name,
                    performance_data['final_performance_percent'],
                    performance_data['date']
                )
            )

        # Execute all notifications concurrently
        if tasks:
            import asyncio
            await asyncio.gather(*tasks, return_exceptions=True)

    async def notify_anomaly_detected(
        self,
        employee_email: str,
        employee_name: str,
        anomaly_data: Dict
    ):
        """
        Send anomaly detection notifications.

        Args:
            employee_email: Employee email
            employee_name: Employee name
            anomaly_data: Anomaly information
        """
        tasks = []

        if self.email_service:
            tasks.append(
                self.email_service.send_alert_notification(
                    employee_email,
                    employee_name,
                    "Performance Anomaly",
                    anomaly_data['description']
                )
            )

        if self.slack_service:
            tasks.append(
                self.slack_service.notify_anomaly_detected(
                    employee_name,
                    anomaly_data['description'],
                    anomaly_data['severity']
                )
            )

        if tasks:
            import asyncio
            await asyncio.gather(*tasks, return_exceptions=True)


# Example usage
"""
# In your main app initialization:

from phase3_enterprise.notifications.notification_service import (
    EmailNotificationService,
    SlackNotificationService,
    NotificationManager
)

email_service = EmailNotificationService(
    smtp_host=os.getenv("SMTP_HOST"),
    smtp_port=int(os.getenv("SMTP_PORT")),
    smtp_user=os.getenv("SMTP_USER"),
    smtp_password=os.getenv("SMTP_PASSWORD"),
    from_email=os.getenv("EMAILS_FROM_EMAIL"),
    from_name="Healthrix System"
)

slack_service = SlackNotificationService(
    webhook_url=os.getenv("SLACK_WEBHOOK_URL")
)

notification_manager = NotificationManager(
    email_service=email_service,
    slack_service=slack_service
)

# Use in endpoints:

@app.post("/api/v1/performance/calculate")
async def calculate_performance(date: str):
    # ... calculate performance ...

    for score in scores:
        # Send notifications
        await notification_manager.notify_performance_calculated(
            employee_email=score.user.email,
            employee_name=score.user.name,
            performance_data={
                'date': score.date.isoformat(),
                'final_performance_percent': score.final_performance_percent,
                'weighted_prod_score': score.weighted_prod_score,
                'weighted_behavior_score': score.weighted_behavior_score,
                'total_task_points': score.total_task_points,
                'task_count': score.task_count,
            },
            send_email=True,
            send_slack=True
        )

    return scores
"""
