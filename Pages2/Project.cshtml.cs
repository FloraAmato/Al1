using System.Collections.Generic;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace CreaProject.Pages
{
    [AllowAnonymous]
    public class ProjectModel : PageModel
    {
        public List<Project> Projects { get; set; }

        public void OnGet()
        {
            Projects = new List<Project>
            {
                new Project
                {
                    Name = "Project 1",
                    Address = "Address 1",
                    Image = ""
                },
            };
        }
    }
}
