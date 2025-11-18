using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CreaProject.Pages;

[AllowAnonymous]
public class Help : PageModel
{
    public void OnGet()
    {
        
    }
}