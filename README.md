## slackalert

Before this alert can be used, you have to enable incoming webhooks in Slack for the community that is going to receive the alert messages.
Look at https://api.slack.com/incoming-webhooks for details on incoming webhooks for Slack

The slackalert add-on is a custom alert to generate Slack messages.

The current version requires you to configure the Trigger setting to "For each result"

When you install the add-on, you can run the setup to configure the Slack URL to connect to the webhook, the hook token and a proxy

When you configure an alert, the add-on requires the search result to contain at least the following information:
 * an alert type
 * a messages
 * channel (optional)
 
The fields that contain this information can be configured in the alert configuration

The third section in the alert configuration contains information that can be used to construct the Slack message.
(for more information on these fields have a look at https://api.slack.com/docs/message-attachments)

In the fourth section the message bar colors are defined based on the alert type

The final section defines additional fields to display in the message based on fields in the search results.