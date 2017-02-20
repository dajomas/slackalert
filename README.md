## slackalert

Before this alert can be used, you have to enable incoming webhooks in Slack for the community that is going to receive the alert messages.
Look at https://api.slack.com/incoming-webhooks for details on incoming webhooks for Slack

The slackalert add-on is a custom alert to generate Slack messages.

If the Trigger setting is set to Once, all result events are combined into a single Slack message. If the Trigger setting is set to For each result, then each result will get its own Slack message.

When using the Trigger setting Once, consider using macro's. This means that in stead of $result.fieldname$ you use {fieldname}. Splunk will substitute $result.fieldname$ with only one of the results from the search. When using {fieldname} the script will replace fieldname with the value from each of the results.

When you install the add-on, you can run the setup to configure default values for new alerts.

Both setup and alert configuration consist of the following sections:
 * Slack connect settings. Here you configure the URL, hook token and proxy settings
 * Mandatory settings. The add-on requires the search result to contain at least a severity field. The fieldname can be configured in the alert and defaults to "severity". Here you can also set either the message field or the message itself
 * Optional settings. To override the channel for the configured webhook
 * Severity color settings. Set the colorbar of the Slack message according to the severity value
 * Additional fields. Any field that is returned by the search can be added to the Slack message
 * Message format settings. The last section in the setup and alert configuration contains information that can be used to construct the Slack message. (for more information on these fields have a look at https://api.slack.com/docs/message-attachments)
