using CreaProject.Areas.Identity.Data;
using CreaProject.Data;
using CreaProject.Models;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.EntityFrameworkCore;
using System;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Threading.Tasks;

namespace CreaProject.Areas.Identity.Pages.Account.Manage
{
    public class IndexModel : PageModel
    {
        private readonly SignInManager<CreaUser> _signInManager;
        private readonly UserManager<CreaUser> _userManager;
        private readonly ApplicationDbContext _context;

        public IndexModel(
            UserManager<CreaUser> userManager,
            SignInManager<CreaUser> signInManager,
            ApplicationDbContext Context
)
        {
            _userManager = userManager;
            _signInManager = signInManager;
            _context = Context;
        }

        [TempData]
        public string StatusMessage { get; set; }

        [BindProperty]
        public DetailsModel Details { get; set; }

        [BindProperty]
        public PasswordModel Password { get; set; }

        [BindProperty]
        public bool CanDelete { get; set; }

        private async Task LoadAsync(CreaUser user)
        {
            var userName = await _userManager.GetUserNameAsync(user);
            var phoneNumber = await _userManager.GetPhoneNumberAsync(user);

            Details = new DetailsModel
            {
                Surname = user.Surname,
                Name = user.Name,
                PhoneNumber = phoneNumber,
                Email = user.Email
            };
        }

        public async Task<IActionResult> OnGetAsync()
        {
            var user = await _userManager.GetUserAsync(User);
            if (user == null)
                return NotFound($"Unable to load user with ID '{_userManager.GetUserId(User)}'.");

            await LoadAsync(user);

            var disputes = await _context
                .Disputes
                .Include(d => d.Goods)
                .Include(d => d.Agents)
                .ThenInclude(a => a.CreaUser)
                .AsNoTracking()
                .ToListAsync();

            var currentUserDisputes = _context
                .Agents.Where(d => d.CreaUserId == user.Id)
                .Select(d => d.DisputeId)
                .ToList();
            var myDisputes = disputes.Where(c => c.OwnerId == user.Id).ToList();
            var agentDisputes = disputes
                .Where(c =>
                    (c.Status == DisputeStatus.Bidding | c.Status == DisputeStatus.Finalizing)
                    && currentUserDisputes.Contains(c.DisputeId)
                )
                .ToList();

            CanDelete = myDisputes.Count == 0 && agentDisputes.Count == 0;

            return Page();
        }

        public async Task<IActionResult> OnPostSaveDetailsAsync()
        {
            var user = await _userManager.GetUserAsync(User);
            if (user == null)
                return NotFound($"Unable to load user with ID '{_userManager.GetUserId(User)}'.");

                if (Details.Surname != user.Surname)
                    user.Surname = Details.Surname;

                if (Details.Name != user.Name)
                    user.Name = Details.Name;

                if (Details.Email != user.Email)
                    user.Email = Details.Email;

                var phoneNumber = await _userManager.GetPhoneNumberAsync(user);
                if (Details.PhoneNumber != phoneNumber)
                {
                    var setPhoneResult = await _userManager.SetPhoneNumberAsync(
                        user,
                        Details.PhoneNumber
                    );
                    if (!setPhoneResult.Succeeded)
                    {
                        var userId = await _userManager.GetUserIdAsync(user);
                        throw new InvalidOperationException(
                            $"Unexpected error occurred setting phone number for user with ID '{userId}'."
                        );
                    }
                }

                await _userManager.UpdateAsync(user);

                await _signInManager.RefreshSignInAsync(user);
                StatusMessage = "Your profile has been updated";
                return RedirectToPage();
        }

        public async Task<IActionResult> OnPostSavePasswordAsync()
        {
            var user = await _userManager.GetUserAsync(User);
            if (user == null)
                return NotFound($"Unable to load user with ID '{_userManager.GetUserId(User)}'.");

            ModelState.Clear();

            if (TryValidateModel(Password, "Password"))
            {
                var result = await _userManager.ChangePasswordAsync(
                    user,
                    Password.CurrentPassword,
                    Password.NewPassword
                );
                if (!result.Succeeded)
                {
                    foreach (var error in result.Errors)
                    {
                        ModelState.AddModelError(string.Empty, error.Description);
                    }
                    await LoadAsync(user);
                    return Page();
                }

                await _signInManager.RefreshSignInAsync(user);
                StatusMessage = "Your password has been changed.";

                return RedirectToPage();
            }
            else
            {
                var errors = ModelState.Where(ms => ms.Key.StartsWith("Password")).SelectMany(ms => ms.Value.Errors).Select(e => e.ErrorMessage).ToList();
                foreach (var error in errors)
                {
                    ModelState.AddModelError(string.Empty, error);
                }
                await LoadAsync(user);
                return Page();
            }
        }

        public Task<IActionResult> OnPostDeleteAsync()
        {
            throw new NotImplementedException();
        }

        public class DetailsModel
        {
            [Required]
            [DataType(DataType.Text)]
            [Display(Name = "Lastname")]
            public string Surname { get; set; }

            [Required]
            [DataType(DataType.Text)]
            [Display(Name = "Firstname")]
            public string Name { get; set; }

            [Phone]
            [DataType(DataType.PhoneNumber)]
            [Display(Name = "Phone number")]
            public string PhoneNumber { get; set; }

            [Required]
            [EmailAddress]
            [DataType(DataType.EmailAddress)]
            [Display(Name = "Email")]
            public string Email { get; set; }
        }

        public class PasswordModel
        {

            [Required]
            [DataType(DataType.Password)]
            [Display(Name = "Current password")]
            public string CurrentPassword { get; set; }

            [Required]
            [StringLength(100, ErrorMessage = "The {0} must be at least {2} and at max {1} characters long.", MinimumLength = 6)]
            [DataType(DataType.Password)]
            [Display(Name = "Password")]
            public string NewPassword { get; set; }

            [DataType(DataType.Password)]
            [Display(Name = "Confirm password")]
            [Compare("NewPassword", ErrorMessage = "The new password and confirmation password do not match.")]
            public string ConfirmPassword { get; set; }
        }
    }
}
