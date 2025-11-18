using System.Collections;
using System.Collections.Generic;
using System.Linq;
using CreaProject.Areas.Identity.Data;
using CreaProject.Authorization;
using CreaProject.Data;
using CreaProject.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Localization;
using System.Threading.Tasks;
using CreaProject.Helpers;
using Microsoft.Build.Framework;
using Microsoft.Extensions.Azure;
using Microsoft.AspNetCore.WebUtilities;
using System.Text;
using Mailjet.Client.Resources;

namespace CreaProject.Pages.Disputes
{
    public class CreateModel : DisputeBasePageModel
    {
        private readonly MailjetService _mailjetService;

        public CreateModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager,
            IStringLocalizer<DisputeBasePageModel> localizer,
            MailjetService mailjetService
        )
            : base(context, authorizationService, userManager, localizer)
        {
            _mailjetService = mailjetService;
        }

        [BindProperty] 
        public Agent Agent { get; set; }
        
        [BindProperty]
        public Good Good { get; set; }

        public Agent CurrentAgent { get; set; }

        [BindProperty]
        public bool ShoudGoToDashboard { get; set; }
        public bool IsCurrentStep { get; set; } = false;

        public async Task<IActionResult> OnGet(int disputeId)
        {
            Dispute existingDispute = await Context.Disputes
                .Include(d => d.Goods)
                .Include(d => d.AgentUtilities)
                .Include(d => d.Agents)
                .ThenInclude(a => a.CreaUser)
                .FirstOrDefaultAsync(d => d.DisputeId == disputeId);

            if (existingDispute != null)
            {
                Dispute = existingDispute;
                CreaUser currentUser = await UserManager.GetUserAsync(User);
                CurrentAgent = existingDispute.Agents.Find(a => a.CreaUserId == currentUser.Id);
                if (Dispute.Status == DisputeStatus.SettingUp) IsCurrentStep = true;
            }
            else
            {
                return RedirectToPage("./Index");
            }

            return Page();
        }


        public async Task<IActionResult> OnPostSaveDisputeAsync(int DisputeId)
        {
            Dispute existingDispute = await Context.Disputes
                .Include(d => d.Goods)
                .Include(d => d.AgentUtilities)
                .Include(d => d.Agents)
                .ThenInclude(a => a.CreaUser)
                .FirstOrDefaultAsync(d => d.DisputeId == DisputeId);

            if (existingDispute == null) return NotFound();
            
            if (Dispute.Agents != null)
            {
                foreach (var agent in Dispute.Agents)
                {
                    CreaUser user = await Context.Users.AsNoTracking().FirstOrDefaultAsync(u => u.Email == agent.Email);
                    if (user == null)
                    {
                        // TODO: invite user
                    }

                    Agent Agent = new()
                    {
                        CreaUserId = user != null ? user.Id : "",
                        Email = agent.Email,
                    };
                    Context.Agents.Add(Agent);
                    await Context.SaveChangesAsync();
                }
            }

            if (Dispute.Goods != null)
            {
                foreach (Good good in Dispute.Goods)
                {
                    Context.Goods.Add(good);
                    await Context.SaveChangesAsync();
                }
            }

            existingDispute.Name = Dispute.Name;
            existingDispute.ResolutionMethod = Dispute.ResolutionMethod;
            if (Dispute.ResolutionMethod == DisputeResolutionMethod.Bids)
            {
                existingDispute.BoundsPercentage = Dispute.BoundsPercentage;
            }
            else
            {
                existingDispute.RatingWeight = Dispute.RatingWeight;
            }

            AuthorizationResult isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                existingDispute,
                DisputeOperations.Update
            );
            if (!isAuthorized.Succeeded)
                return new ChallengeResult();

            Context.Disputes.Update(existingDispute);
            await Context.SaveChangesAsync();

            Dispute = existingDispute;
            if (ShoudGoToDashboard)
            {
                return RedirectToPage("./Index");
            }
            else
            {
                return await OnGet(DisputeId);
            }
            
        }

        public async Task<IActionResult> OnPostAddAgentAsync(int DisputeId)
        {
            Dispute dispute = await Context
                .Disputes.AsNoTracking()
                .Include(d => d.Agents)
                .FirstOrDefaultAsync(d => d.DisputeId == DisputeId);

            if (dispute == null)
                return NotFound();

            AuthorizationResult isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                dispute,
                DisputeOperations.Update
            );

            if (!isAuthorized.Succeeded)
                return new ChallengeResult();

            if (dispute.Agents.Any(a => a.Email == Agent.Email))
            {
                ModelState.AddModelError(string.Empty, "There is already an agent with this email for this dispute");
                return RedirectToPage(new { dispute.DisputeId });
            }

            Agent.DisputeId = DisputeId;

            CreaUser user = await Context
                .Users.AsNoTracking()
                .FirstOrDefaultAsync(u => u.Email == Agent.Email);

            bool ShouldCreate = false;

            if (user != null)
            {
                Agent.CreaUserId = user.Id;
                Agent.CreaUser = user;

                Context.Attach(user);
            }
            else
            {
                user = new CreaUser();
                user.Email = Agent.Email;
                user.UserName = Agent.Email;
                var securityToken = await UserManager.CreateSecurityTokenAsync(user);
                var result = await UserManager.CreateAsync(user);

                if (!result.Succeeded)
                {
                    return RedirectToPage(new { dispute.DisputeId, Error = $"Couldn't add new Agent : {result.Errors.FirstOrDefault()?.Description ?? "No error description available"}" });
                    //TODO: Invite user
                }
                ShouldCreate = true;
                Agent.CreaUserId = user.Id;
            }

            Context.Agents.Add(Agent);
            await Context.SaveChangesAsync();
            if (ShouldCreate)
            {
                string code = await UserManager.GeneratePasswordResetTokenAsync(user);
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
                            { "callbackUrl", callbackUrl }
                        };

                bool mailSent = await _mailjetService.SendEmailAsync(Agent.Email, "Welcome on the CREA2 platform - Invitation to participate to a new dispute", "InviteNewAgent", mailVariables);
            }
            else
            {
                var callbackUrl = Url.Page(
                   $"/Dispute/Create/{dispute.DisputeId}",
                    pageHandler: null,
                    null,
                    protocol: Request.Scheme);

                var mailVariables = new Dictionary<string, string>
                        {
                            { "name", user.UserName },
                            { "callbackUrl", callbackUrl }
                        };

                bool mailSent = await _mailjetService.SendEmailAsync(Agent.Email, "Invitation to participate to a new dispute", "InviteAgent", mailVariables);
            }

            return RedirectToPage(new { dispute.DisputeId });
        }

        public async Task<IActionResult> OnPostDeleteAgentAsync(int AgentId)
        {
            Agent agent = await Context.Agents.FindAsync(AgentId);

            if (agent == null) return NotFound();

            Dispute dispute = await Context.Disputes.Include(d => d.Agents)
                .FirstOrDefaultAsync(d => d.DisputeId == agent.DisputeId);

            if (dispute == null) return NotFound();

            AuthorizationResult isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                dispute,
                DisputeOperations.Update
            );

            if (!isAuthorized.Succeeded) return new ChallengeResult();

            Context.Agents.Remove(agent);
            await Context.SaveChangesAsync();

            return RedirectToPage(new { dispute.DisputeId });
        }

        public async Task<IActionResult> OnPostEditAgent(int agentId)
        {
            Agent existingAgent = await Context.Agents.FindAsync(agentId);
            if (existingAgent == null) return NotFound();

            Dispute dispute = await Context.Disputes.Include(d => d.Agents)
                .FirstOrDefaultAsync(d => d.DisputeId == existingAgent.DisputeId);
            if (dispute == null) return NotFound();

            if (existingAgent.Email != Agent.Email)
            {
                if (dispute.Agents.Any(a => a.Email == Agent.Email))
                {
                    ModelState.AddModelError(string.Empty,
                        "There is already an agent with this email for this dispute");
                    return RedirectToPage(new { dispute.DisputeId });
                }

                CreaUser newUser = await Context.Users.AsNoTracking().FirstOrDefaultAsync(u => u.Email == Agent.Email);

                existingAgent.CreaUser = null;
                existingAgent.CreaUserId = null;

                if (newUser != null)
                {
                    existingAgent.CreaUserId = newUser.Id;
                    existingAgent.CreaUser = newUser;

                    Context.Attach(newUser);
                }
                else
                {
                    //TODO: Invite User
                    var user = new CreaUser();
                    user.Email = Agent.Email;
                    user.UserName = Agent.Email;
                    var securityToken = await UserManager.CreateSecurityTokenAsync(user);
                    var result = await UserManager.CreateAsync(user);

                    if (!result.Succeeded)
                    {
                        return RedirectToPage(new { dispute.DisputeId, Error = $"Couldn't add new Agent : {result.Errors.FirstOrDefault()?.Description ?? "No error description available"}" });
                        //TODO: Invite user
                    }

                    string code = await UserManager.GeneratePasswordResetTokenAsync(user);
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
                            { "callbackUrl", callbackUrl }
                        };

                    bool mailSent = await _mailjetService.SendEmailAsync(Agent.Email, "Welcome on the CREA2 platform - Invitation to participate to a new dispute", "InviteNewAgent", mailVariables);
                    

                    Agent.CreaUserId = user.Id;
                    var agent = Context.Agents.First(c => c.AgentId == agentId);
                    agent.CreaUserId = user.Id;
                    Context.Agents.Update(agent);
                    Context.SaveChanges();
                }

                existingAgent.Email = Agent.Email;
            }

            existingAgent.ShareOfEntitlement = Agent.ShareOfEntitlement;


            await Context.SaveChangesAsync();
            return RedirectToPage(new { dispute.DisputeId });
        }

        public async Task<IActionResult> OnPostAddGoodAsync(int disputeId)
        {
            Dispute dispute = await Context
                .Disputes.Include(d => d.Agents).AsNoTracking()
                .FirstOrDefaultAsync(d => d.DisputeId == disputeId);

            if (dispute == null)
                return NotFound();

            AuthorizationResult isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                dispute,
                DisputeOperations.Update
            );

            if (!isAuthorized.Succeeded)
                return new ChallengeResult();

            Good.DisputeId = dispute.DisputeId;

            Context.Goods.Add(Good);
            
            foreach (Agent agent in dispute.Agents)
            {
                agent.Validated = ValidatedSteps.None;
            }
            
            await Context.SaveChangesAsync();
            
            return RedirectToPage(new { dispute.DisputeId });
        }

        public async Task<IActionResult> OnPostEditGoodAsync(int goodId)
        {
            Good existingGood = await Context.Goods.FindAsync(goodId);
            if (existingGood == null) return NotFound();
            
            Dispute dispute = await Context.Disputes.Include(d => d.Goods)
                .Include(d => d.Agents)
                .FirstOrDefaultAsync(d => d.DisputeId == existingGood.DisputeId);
            if (dispute == null) return NotFound();
            
            AuthorizationResult isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                dispute,
                DisputeOperations.Update
            );

            if (!isAuthorized.Succeeded) return new ChallengeResult();

            existingGood.Name = Good.Name;
            existingGood.EstimatedValue = Good.EstimatedValue;
            existingGood.Indivisible = Good.Indivisible;
            
            foreach (Agent agent in dispute.Agents)
            {
                agent.Validated = ValidatedSteps.None;
            }

            await Context.SaveChangesAsync();

            return RedirectToPage(new { dispute.DisputeId });
        }

        public async Task<IActionResult> OnPostDeleteGoodAsync(int goodId)
        {
            Good good = await Context.Goods.FindAsync(goodId);
            if (good == null) return NotFound();
            
            Dispute dispute = await Context.Disputes.Include(d => d.Goods)
                .Include(d => d.Agents)
                .FirstOrDefaultAsync(d => d.DisputeId == good.DisputeId);
            if (dispute == null) return NotFound();
            
            AuthorizationResult isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                dispute,
                DisputeOperations.Update
            );

            if (!isAuthorized.Succeeded) return new ChallengeResult();

            Context.Goods.Remove(good);

            foreach (Agent agent in dispute.Agents)
            {
                agent.Validated = ValidatedSteps.None;
            }
            
            await Context.SaveChangesAsync();
            
            return RedirectToPage(new { dispute.DisputeId });
        }

        public async Task<IActionResult> OnPostValidateDisputeAsync(int agentId)
        {
            CreaUser currentUser = await UserManager.GetUserAsync(User);
            
            Agent validatingAgent = await Context.Agents.FirstOrDefaultAsync(a => a.CreaUserId == currentUser.Id && a.DisputeId == Dispute.DisputeId);
            await Context.Agents.Where(c => c.DisputeId == Dispute.DisputeId).ForEachAsync(c => c.Validated = ValidatedSteps.Setup);
            if (validatingAgent == null) return NotFound();

            validatingAgent.Validated = ValidatedSteps.Setup;

            await Context.SaveChangesAsync();

            Dispute currentDispute = await Context.Disputes
                .Include(d => d.Goods)
                .Include(d => d.Agents)
                .FirstOrDefaultAsync(d => d.DisputeId == Dispute.DisputeId);

            if (currentDispute == null) return NotFound();

            // Now rule implies validation of one is validation of all
            bool allAgentsValidated = true;



            

            currentDispute.ResolutionMethod = Dispute.ResolutionMethod;

            if (currentDispute.ResolutionMethod == DisputeResolutionMethod.Bids)
            {            
                IEnumerable<Bid> bids = currentDispute.Agents.SelectMany(agent => 
                    currentDispute.Goods.Select(good => 
                        new Bid
                        {
                            AgentId = agent.AgentId,
                            Agent = agent,
                            GoodId = good.GoodId,
                            Good = good,
                            Dispute = currentDispute,
                            DisputeId = currentDispute.DisputeId,
                            BidValue = 0M
                        }
                    )
                ).ToList();
                Context.Bids.AddRange(bids);
            }
            else
            {
                IEnumerable<Rate> rates = currentDispute.Agents.SelectMany(agent => 
                    currentDispute.Goods.Select(good => 
                        new Rate
                        {
                            Agent = agent,
                            AgentId = agent.AgentId,
                            Good = good,
                            GoodId = good.GoodId,
                            Dispute = currentDispute,
                            DisputeId = currentDispute.DisputeId,
                            RateValue = 1
                        }
                    )
                ).ToList();
                Context.Rates.AddRange(rates);
            }
            
            currentDispute.Status = DisputeStatus.Bidding;
            if (Dispute.ResolutionMethod == DisputeResolutionMethod.Bids)
            {
                currentDispute.BoundsPercentage = Dispute.BoundsPercentage;
            }
            else
            {
                currentDispute.RatingWeight = Dispute.RatingWeight;
            }
            
            await Context.SaveChangesAsync();


            if (!allAgentsValidated)
            {
                Dispute = currentDispute;
                return Page();
            }

            return Redirect($"/Disputes/Bids/{currentDispute.DisputeId}");
        }
    }
}
