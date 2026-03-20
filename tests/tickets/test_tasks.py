from unittest.mock import patch

from apps.tickets.tasks import send_ticket_email


class TestSendTicketEmail:

    @patch('apps.tickets.tasks.send_mail')
    def test_sends_email_with_correct_data(self, mock_send_mail):
        send_ticket_email(
            email='test@test.com',
            ticket_id='abc-123',
            username='daviots',
        )
        mock_send_mail.assert_called_once()
        call_kwargs = mock_send_mail.call_args
        assert 'test@test.com' in str(call_kwargs)
        assert 'daviots' in str(call_kwargs)
        assert 'abc-123' in str(call_kwargs)

    @patch('apps.tickets.tasks.send_mail')
    def test_email_subject_is_correct(self, mock_send_mail):
        send_ticket_email(
            email='test@test.com',
            ticket_id='abc-123',
            username='daviots',
        )
        subject = mock_send_mail.call_args[1].get('subject') or mock_send_mail.call_args[0][0]
        assert 'Ticket' in subject