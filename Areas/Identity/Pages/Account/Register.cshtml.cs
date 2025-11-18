using CreaProject.Areas.Identity.Data;
using CreaProject.Data;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.AspNetCore.WebUtilities;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CreaProject.Models;

namespace CreaProject.Areas.Identity.Pages.Account
{
    [AllowAnonymous]
    public class RegisterModel : PageModel
    {
        private readonly ApplicationDbContext _context;

        //private readonly IEmailSender<CreaUser> _emailSender;
        private readonly ILogger<RegisterModel> _logger;
        private readonly SignInManager<CreaUser> _signInManager;
        private readonly UserManager<CreaUser> _userManager;

        public RegisterModel(
            ApplicationDbContext context,
            UserManager<CreaUser> userManager,
            SignInManager<CreaUser> signInManager,
            ILogger<RegisterModel> logger
        )
        //IEmailSender<CreaUser> emailSender)
        {
            _context = context;
            _userManager = userManager;
            _signInManager = signInManager;
            _logger = logger;
            //  _emailSender = emailSender;
        }

        [BindProperty]
        public InputModel Input { get; set; }

        public string ReturnUrl { get; set; }

        public IList<AuthenticationScheme> ExternalLogins { get; set; }

        public async Task OnGetAsync(string returnUrl = null)
        {
            ReturnUrl = returnUrl;
            ExternalLogins = (
                await _signInManager.GetExternalAuthenticationSchemesAsync()
            ).ToList();
        }

        public async Task<IActionResult> OnPostAsync(string returnUrl = null)
        {
            returnUrl = returnUrl ?? Url.Content("~/Disputes");
            ExternalLogins = (
                await _signInManager.GetExternalAuthenticationSchemesAsync()
            ).ToList();
            if (!ModelState.IsValid) return Page();
            CreaUser user = new CreaUser
            {
                Surname = Input.Surname,
                Name = Input.Name,
                UserName = Input.Email,
                Email = Input.Email
            };
            IdentityResult result = await _userManager.CreateAsync(user, Input.Password);
            if (result.Succeeded)
            {
                _logger.LogInformation("User created a new account with password.");

                string code = await _userManager.GenerateEmailConfirmationTokenAsync(user);
                code = WebEncoders.Base64UrlEncode(Encoding.UTF8.GetBytes(code));
                string callbackUrl = Url.Page(
                    "/Account/ConfirmEmail",
                    null,
                    new
                    {
                        area = "Identity",
                        userId = user.Id,
                        code
                    },
                    Request.Scheme
                );

                //await _emailSender.SendEmailAsync(Input.Email, "Confirm your email",
                //    $"Please confirm your account by <a href='{HtmlEncoder.Default.Encode(callbackUrl)}'>clicking here</a>.");

                List<Agent> agents = _context.Agents.Where(a => a.Email == Input.Email).ToList();
                foreach (Agent agent in agents)
                {
                    agent.CreaUser = user;
                    _context.Attach(agent).State = EntityState.Modified;
                }

                await _context.SaveChangesAsync();

                if (_userManager.Options.SignIn.RequireConfirmedAccount)
                {
                    return RedirectToPage("RegisterConfirmation", new { email = Input.Email });
                }

                await _signInManager.SignInAsync(user, false);
                return LocalRedirect(returnUrl);
            }

            foreach (var error in result.Errors)
                ModelState.AddModelError(string.Empty, error.Description);

            // If we got this far, something failed, redisplay form
            return Page();
        }

        public class InputModel
        {
            [Required]
            [Display(Name = "Surname")]
            public string Surname { get; set; }

            [Required]
            [Display(Name = "Name")]
            public string Name { get; set; }

            [Required]
            [EmailAddress]
            [Display(Name = "Email")]
            public string Email { get; set; }

            [Required]
            [StringLength(
                100,
                ErrorMessage = "The {0} must be at least {2} and at max {1} characters long.",
                MinimumLength = 6
            )]
            [DataType(DataType.Password)]
            [Display(Name = "Password")]
            public string Password { get; set; }

            [DataType(DataType.Password)]
            [Display(Name = "Confirm password")]
            [Compare(
                "Password",
                ErrorMessage = "The password and confirmation password do not match."
            )]
            public string ConfirmPassword { get; set; }

            //[Display(Name = "I agree with privacy policy")]
            //[Range(typeof(bool), "true", "true", ErrorMessage = "You gotta tick the box!")]
            //public bool PrivacyPolicy { get; set; }

            [RegularExpression(@"^true", ErrorMessage = "The checkbox is required")]
            public string PrivacyPolicy { get; set; }

            /*            [RegularExpression(@"^true", ErrorMessage = "The checkbox is required")]
                        public string Older18 { get; set; }
            */
            //[Display(Name = "I am 18 years old or over")]
            //[Range(typeof(bool), "true", "true", ErrorMessage = "You gotta tick the box!")]
            //public bool Older18 { get; set; }
        }
    }
}
