using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Threading.Tasks;
using CreaProject.Helpers;
using Mailjet.Client.Resources;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CreaProject.Pages
{
    [AllowAnonymous]
    public class ContactModel : PageModel
    {
        [BindProperty]
        public InputModel Input { get; set; }

        public bool MailSent { get; set; } = false;

        [TempData]
        public string ErrorMessage { get; set; }

        public class InputModel
        {
            [Required]
            public string Name { get; set; }

            [Required]
            [EmailAddress]
            public string Email { get; set; }

            [Required]
            [Display(Name = "Comment or message")]
            public string Message { get; set; }
        }

        private readonly MailjetService _mailjetService;

        public ContactModel(MailjetService mailjetService)
        {
            _mailjetService = mailjetService;
        }

        public void OnGet() { }

        public async Task<IActionResult> OnPostContactAsync() {
            var mailVariables = new Dictionary<string, string>
            {
                { "message",this.Input.Message },
                { "email", this.Input.Email },
                { "username", this.Input.Name }
            };

           await  _mailjetService.SendEmailAsync("crea_project@proton.me", "New message from the Contact Form of CREA2", "ContactMessage", mailVariables);
            this.MailSent = true;
            return Page();
        }
    }
}
