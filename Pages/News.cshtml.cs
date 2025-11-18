using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CreaProject.Pages
{
    [AllowAnonymous]
    public class NewsModel : PageModel
    {
        public void OnGet() { }
    }
}
