using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Text;
using System.Text.Encodings.Web;
using System.Threading.Tasks;
using CreaProject.Areas.Identity.Data;
using CreaProject.Helpers;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.AspNetCore.WebUtilities;

namespace CreaProject.Areas.Identity.Pages.Account
{
    [AllowAnonymous]
    public class ForgotPasswordModel : PageModel
    {
        private readonly UserManager<CreaUser> _userManager;
        private readonly MailjetService _mailjetService;
        
        public ForgotPasswordModel(
            UserManager<CreaUser> userManager, MailjetService mailjetService
        )
        {
            _userManager = userManager;
            _mailjetService = mailjetService;
        }

        [BindProperty]
        public InputModel Input { get; set; }

        public bool EmailSent { get; set; } = false;

        public class InputModel
        {
            [Required]
            [EmailAddress]
            public string Email { get; set; }
        }

        public async Task<IActionResult> OnPostAsync()
        {
            if (!ModelState.IsValid) return Page();
            var user = await _userManager.FindByEmailAsync(Input.Email);
            if (user == null)
            {
                EmailSent = true;
                return Page();
            }
            
            string code = await _userManager.GeneratePasswordResetTokenAsync(user);
            code = WebEncoders.Base64UrlEncode(Encoding.UTF8.GetBytes(code));
            var callbackUrl = Url.Page(
                "/Account/ResetPassword",
                pageHandler: null,
                values: new { area = "Identity", code },
                protocol: Request.Scheme
            );

            var mailVariables = new Dictionary<string, string>
            {
                { "name", user.UserName },
                { "message", "Ceci est un message de test" },
                { "callbackUrl", callbackUrl }
            };

            bool mailSent = await _mailjetService.SendEmailAsync(Input.Email, "Reset Password", "ResetPassword", mailVariables);
            if (!mailSent)
            {
                EmailSent = false;
                return Page();
            }
            EmailSent = true;
            return Page();
            // return RedirectToPage("./ForgotPasswordConfirmation");
        }
    }
}
