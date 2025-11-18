using CreaProject.Data;
using CreaProject.Helpers;
using CreaProject.Models;
using Mailjet.Client.Resources;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using static System.Net.WebRequestMethods;

namespace CreaProject.Controllers
{
    public class VisioController : Controller
    {

        private MailjetService _mailjetService;
        private ApplicationDbContext _context { get; }

        public VisioController(
            MailjetService mailjetService,
            ApplicationDbContext dbContext)
        {
            _mailjetService = mailjetService;
            _context = dbContext;
        }

        public IActionResult Index()
        {
            return View();
        }

        private string GenerateRoomName()
        {
            return "CreaMeeting_" + System.Guid.NewGuid();
        }

        private string MeetingUrl()
        {
            return $"https://meet.jit.si/{GenerateRoomName()}";
        }

        [HttpPost]
        [Authorize]
        public async Task<IActionResult> SendInvite(int DisputeId, string SelectedMediator, string[] SelectedAgents)
        {
            var meetingUrl = MeetingUrl();
            var dispute = _context.Disputes.Include(c => c.Agents).FirstOrDefault(c => c.DisputeId == DisputeId);

            if (dispute != null)
            {
              

                var mailVariables = new Dictionary<string, string>
                        {
                            { "name", User.Identity.Name },
                            { "callbackUrl", meetingUrl },
                            {"disputeName", dispute.Name }
                        };

                bool mailSent = await _mailjetService.SendEmailAsync(SelectedMediator, "Invitation to join a visio conference CREA 2", "VisioInvite", mailVariables);


                foreach (var item in SelectedAgents)
                {
                    if (User.Identity.Name != item)
                    {
                         mailSent = await _mailjetService.SendEmailAsync(item, "Invitation to join a visio conference CREA 2", "VisioInvite", mailVariables);
                    }
                }

            }

            return Redirect(meetingUrl);
        }
    }
}
