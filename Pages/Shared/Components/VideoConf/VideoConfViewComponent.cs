using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using CreaProject.Data;
using CreaProject.Helpers;
using CreaProject.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace CreaProject.Pages.Shared;

public class Country
{
    public string Name { get; set; }
    public string Code { get; set; }
    public List<Mediator> Mediators { get; set; } = new();
}

public class Mediator
{
    public string name;
    public string email;
    public string linkedInProfile;

}

public class VideoConfViewModel
{
    public List<Agent> Agents { get; set; }
    public List<Country> MediatorsPerCountry { get; set; } 

    public int DisputeId { get; set; }
}

public class VideoConfViewComponent : ViewComponent
{
    private readonly ApplicationDbContext _context;
    private readonly MailjetService _mailjetService;

    public VideoConfViewComponent(ApplicationDbContext context, MailjetService mailjetService)
    {
        _context = context;
        _mailjetService = mailjetService;
    }
    
    public async Task<IViewComponentResult> InvokeAsync(int disputeId)
    {
        List<Agent> agents = await _context.Agents.Where(a => a.DisputeId == disputeId).Include(c => c.CreaUser).ToListAsync();

        List<Country> countries = new List<Country>();
        countries.Add(new Country { Name = "Belgium", Code="BE" });
        countries.Add(new Country { Name = "Croatia", Code="HR" });
        countries.Add(new Country { Name = "Estonia", Code="EE" });
        countries.Add(new Country
        {
            Name = "Italy",
            Code="IT",
            Mediators = new List<Mediator>
            {
                new Mediator{name = "Antonella Addeo", email = "antonella@mailinator.com" , linkedInProfile = "https://www.linkedin.com/in/antonella-addeo-4759a06a?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app"},
                new Mediator{name = "Paola Giacalone", email = "paola@mailinator.com" , linkedInProfile = "https://www.linkedin.com/in/paola-giacalone-200aa4158/?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app"},

            }
        });
        countries.Add(new Country { Name = "Lithuania", Code="LI" });
        countries.Add(new Country { Name = "Slovenia", Code="SL" });
      

        VideoConfViewModel model = new VideoConfViewModel
        {
            Agents = agents,
            MediatorsPerCountry = countries,
            DisputeId = disputeId
        };
        
        return View(model);
    }

   
}