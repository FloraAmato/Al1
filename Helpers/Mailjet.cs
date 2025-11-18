using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Mailjet.Client;
using Mailjet.Client.Resources.SMS;
using Mailjet.Client.TransactionalEmails;
using Mailjet.Client.TransactionalEmails.Response;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Mjml.Net;

namespace CreaProject.Helpers;

public class MailjetService
{
    private readonly IConfiguration _configuration;
    private readonly ILogger<MailjetService> _logger;
    private readonly IMjmlRenderer _mjmlRenderer;

    public MailjetService(IConfiguration configuration, ILogger<MailjetService> logger)
    {
        _configuration = configuration;
        _logger = logger;
        _mjmlRenderer = new MjmlRenderer();
    }

    public async Task<bool> SendEmailAsync(string toEmail, string subject, string templateName, Dictionary<string, string> variables)
    {
        try
        {
            string templatePath = Path.Combine(Directory.GetCurrentDirectory(), "Resources/MailTemplates", $"{templateName}.mjml");
            string mjmlContent = await File.ReadAllTextAsync(templatePath);

            foreach (var variable in variables)
            {
                mjmlContent = mjmlContent.Replace($"{{{variable.Key}}}", variable.Value);
            }

            RenderResult renderResult = _mjmlRenderer.Render(mjmlContent);
            if (renderResult.Errors.Count > 0)
            {
                throw new Exception("Error while converting MJML to HTML");
            }

            string htmlContent = renderResult.Html;
            
            MailjetClient client = new MailjetClient(_configuration["MailJetApiKey"], _configuration["MailJetApiSecret"]);
            _logger.LogInformation("key : "+_configuration["MailJetApiKey"]);
            _logger.LogInformation("secret:"+_configuration["MailJetApiSecret"]);
            TransactionalEmail email = new TransactionalEmailBuilder()
                .WithFrom(new SendContact("pierre@seraphin.legal"))
                .WithSubject(subject)
                .WithHtmlPart(htmlContent)
                .WithTo(new SendContact(toEmail))
                .Build();
            TransactionalEmailResponse response = await client.SendTransactionalEmailAsync(email);

            MessageResult message = response.Messages[0];

            bool result = message.Status.Equals("success", System.StringComparison.CurrentCultureIgnoreCase);
            if (result)
                _logger.LogInformation("Email has been sent successfully");
            else
                _logger.LogError($"Cannot send email : {string.Join(",", message.Errors.Select(c => c.ErrorMessage))}");


            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error while trying to send an email");
            return false;
        }
    }
}