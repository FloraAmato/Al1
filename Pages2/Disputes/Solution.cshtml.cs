using CreaProject.Areas.Identity.Data;
using CreaProject.Authorization;
using CreaProject.Data;
using CreaProject.Models;
using Cureos.Numerics.Optimizers;
using Google.OrTools.LinearSolver;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Localization;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using CreaProject.Helpers;
using Constraint = Google.OrTools.LinearSolver.Constraint;

namespace CreaProject.Pages.Disputes
{
    public class SolutionModel : DisputeBasePageModel
    {
        private readonly BlockchainHelper _blockchainHelper;
        public SolutionModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager,
            IStringLocalizer<DisputeBasePageModel> localizer,
            BlockchainHelper blockchainHelper)
            : base(context, authorizationService, userManager, localizer) 
        {
            _blockchainHelper = blockchainHelper;
        }

        [BindProperty]
        public List<List<Variable>> ProblemVars { get; private set; }

        //[BindProperty]
        public OptimizationSummary ResultNash { get; private set; }

        [BindProperty]
        public List<AgentUtility> CurrentAgentUtilities { get; private set; }

        private List<List<AgentUtility>> AgentsUtilities { get; set; }
        private List<RestrictedAssignment> RestrictedAssignments { get; set; }
        private List<Good> RestrictedGoods { get; set; }

        public bool IsFullyValidated { get; set; } = false;

        public string BlockchainUrl { get; set; } = "https://chain.scan2project.org";

        public async Task<IActionResult> OnGetAsync(int disputeId)
        {
            Dispute = await Context
                .Disputes.AsNoTracking()
                .Include(d => d.Agents)
                .FirstOrDefaultAsync(m => m.DisputeId == disputeId);

            if (Dispute == null)
                return NotFound();

            if (!( Dispute.Status.Equals(DisputeStatus.Finalizing) || 
                Dispute.Status.Equals(DisputeStatus.Finalized) || 
                Dispute.Status.Equals(DisputeStatus.Rejected)))
                return new ForbidResult();
            
            if (Dispute.ResolutionMethod.Equals(DisputeResolutionMethod.Ratings))
                SolveRating(disputeId);
            else
            {
                SolveBids(disputeId);
            }
            
            IsFullyValidated = Dispute.Agents.All(a => a.Validated == ValidatedSteps.Agreement);

            if (IsFullyValidated && string.IsNullOrWhiteSpace(Dispute.BlockId))
            {
              var response = await  _blockchainHelper.AnchorData(this.User.Identity.Name, new { dispute = Dispute });
             
                var dis = Context.Disputes.FirstOrDefault(
                    c => c.DisputeId == Dispute.DisputeId);
                dis.BlockId = response;       
                Context.Update(dis);
                Context.SaveChanges();
                Dispute.BlockId = response;
            }


            return Page();
        }

        public async Task<IActionResult> OnPostConfirmSolutionAsync(int disputeId)
        {
            if (!ModelState.IsValid)
                return RedirectToPage("/Disputes", new { disputeId });

            Dispute dispute = await Context
                .Disputes.Include(d => d.Agents).AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == disputeId);

            if (dispute == null)
                return NotFound();

            AuthorizationResult isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                dispute,
                DisputeOperations.Update
            );
            if (!isAuthorized.Succeeded)
                return new ChallengeResult();
            
            CreaUser currentUser = await UserManager.GetUserAsync(User);

            Agent validatingAgent = dispute.Agents.FirstOrDefault(c => c.CreaUserId == currentUser.Id);  //await Context.Agents.FirstOrDefaultAsync(a => a.CreaUserId == currentUser.Id && a.DisputeId == Dispute.DisputeId);

            validatingAgent.Validated = ValidatedSteps.Agreement;
            //Context.Agents.Update(validatingAgent);
            //Context.SaveChanges();


            bool allAgentsValidated = dispute.Agents.Where(c => c.DisputeId == dispute.DisputeId).All(a => a.Validated == ValidatedSteps.Agreement || a.Validated == ValidatedSteps.Disagreement);

            if (allAgentsValidated)
            {
                dispute.Status = DisputeStatus.Finalized;

            }

            Context.Disputes.Update(dispute);
            await Context.SaveChangesAsync();

            return Redirect("/Disputes");
        }

        public async Task<IActionResult> OnPostRejectSolutionAsync(int disputeId)
        {
            if (!ModelState.IsValid)
                return RedirectToPage("/Disputes");

            Dispute dispute = await Context
                .Disputes
                .AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == disputeId);

            if (dispute == null)
                return NotFound();

            AuthorizationResult isAuthorized = await AuthorizationService.AuthorizeAsync(
                User,
                dispute,
                DisputeOperations.Update
            );
            if (!isAuthorized.Succeeded)
                return new ChallengeResult();
            
            CreaUser currentUser = await UserManager.GetUserAsync(User);
            
            Agent validatingAgent = await Context.Agents.FirstOrDefaultAsync(a => a.CreaUserId == currentUser.Id && a.DisputeId == Dispute.DisputeId);

            validatingAgent.Validated = ValidatedSteps.Disagreement;

            dispute.Status = DisputeStatus.Rejected;
            Context.Disputes.Update(dispute);
            await Context.SaveChangesAsync();

            return RedirectToPage("/Disputes");
        }
        
        
        private void SolveRating(int id)
        {
            Dispute = Context
                .Disputes.Include(d => d.Agents)
                .Include(d => d.Goods)
                .Include(d => d.AgentUtilities)
                .ThenInclude(u => u.Good)
                .Include(d => d.RestrictedAssignments)
                .ThenInclude(u => u.Good)
                .AsNoTracking()
                .FirstOrDefault(m => m.DisputeId == id);

            if (Dispute == null) return;

            Dispute.Agents = Context
                .Agents.Include(a => a.CreaUser)
                .Where(a => a.DisputeId == id)
                .ToList();

            List<List<AgentUtility>> agentsUtilities = Dispute.Agents.Select(agent => Dispute.Goods.Select(good => Dispute.AgentUtilities.FirstOrDefault(u => u.AgentId == agent.AgentId && u.GoodId == good.GoodId)).ToList()).ToList();

            List<RestrictedAssignment> restrictedAssignments = Dispute.RestrictedAssignments.ToList();

            List<Good> restrictedGoods = Dispute
                .RestrictedAssignments.Select(ra => ra.Good)
                .Distinct()
                .ToList();

            int totalGoodsCount = Dispute.Goods.Count + restrictedGoods.Count;

            Solver solver = Solver.CreateSolver("CBC_MIXED_INTEGER_PROGRAMMING");

            int i,
                j;
            ProblemVars = [];
            for (i = 0; i < Dispute.Agents.Count; i++)
            {
                List<Variable> zRow = [];
                for (j = 0; j < Dispute.Goods.Count; j++)
                {
                    zRow.Add(Dispute.Goods[j].Indivisible
                        ? solver.MakeIntVar(0.0, 1.0, "z" + (i + 1) + (j + 1))
                        : solver.MakeNumVar(0.0, 1.0, "z" + (i + 1) + (j + 1)));
                }

                for (j = 0; j < restrictedGoods.Count; j++)
                    zRow.Add(
                        solver.MakeNumVar(
                            0.0,
                            1.0,
                            "z" + (i + 1) + (j + Dispute.Goods.Count + 1)
                        )
                    );

                ProblemVars.Add(zRow);
            }

            Variable t = solver.MakeNumVar(0.0, double.PositiveInfinity, "t");

            List<List<decimal>> coefficients = [];
            for (i = 0; i < Dispute.Agents.Count; i++)
            {
                List<decimal> coefficientsRow = [];

                Dispute.Agents[i].Dispute = Dispute;
                decimal weight = (decimal)Dispute.Agents[i].ShareOfEntitlement / 100;

                decimal goodsUtilitiesSum = 0;

                for (j = 0; j < Dispute.Goods.Count; j++)
                    goodsUtilitiesSum += agentsUtilities[i][j].Utility;

                for (j = 0; j < restrictedGoods.Count; j++)
                    goodsUtilitiesSum += restrictedGoods[j].EstimatedValue;

                for (j = 0; j < totalGoodsCount; j++)
                {
                    decimal temp;

                    if (j < Dispute.Goods.Count)
                    {
                        temp = agentsUtilities[i][j].Utility / (goodsUtilitiesSum * weight);
                    }
                    else
                    {
                        temp =
                            restrictedGoods[j - Dispute.Goods.Count].EstimatedValue
                            / (goodsUtilitiesSum * weight);
                    }

                    coefficientsRow.Add(temp);
                }

                coefficients.Add(coefficientsRow);
            }

            List<Constraint> constraints = [];
            for (j = 0; j < totalGoodsCount; j++)
            {
                constraints.Add(solver.MakeConstraint(1.0, 1.0));
                for (i = 0; i < Dispute.Agents.Count; i++)
                {
                    constraints[j].SetCoefficient(ProblemVars[i][j], 1);
                }
            }

            for (i = 0; i < Dispute.Agents.Count; i++)
            {
                constraints.Add(solver.MakeConstraint(0.0, double.PositiveInfinity));

                for (j = 0; j < totalGoodsCount; j++)
                {
                    constraints[i + totalGoodsCount]
                        .SetCoefficient(ProblemVars[i][j], (double)coefficients[i][j]);
                }

                constraints[i + totalGoodsCount].SetCoefficient(t, -1);
            }

            for (i = 0; i < restrictedAssignments.Count; i++)
            {
                double assignedShare =
                    (double)restrictedAssignments[i].ShareOfEntitlement / 100;
                int assignedGoodId = restrictedAssignments[i].GoodId - 1;
                int recipientAgentId = restrictedAssignments[i].AgentId - 1;

                constraints.Add(solver.MakeConstraint(assignedShare, assignedShare));
                constraints[i + totalGoodsCount + Dispute.Agents.Count]
                    .SetCoefficient(ProblemVars[recipientAgentId][assignedGoodId], 1);
            }

            Objective objective = solver.Objective(); 
            objective.SetCoefficient(t, 1); 
            objective.SetMaximization();

            solver.Solve();
        }

        private void SolveBids(int id)
        {
            Dispute = Context
                .Disputes.Include(d => d.Agents)
                .Include(d => d.Goods)
                .Include(d => d.AgentUtilities)
                .ThenInclude(u => u.Good)
                .Include(d => d.RestrictedAssignments)
                .ThenInclude(u => u.Good)
                .AsNoTracking()
                .FirstOrDefault(m => m.DisputeId == id);

            if (Dispute != null)
            {
                Dispute.Agents = Context
                    .Agents.Include(a => a.CreaUser)
                    .Where(a => a.DisputeId == id)
                    .ToList();

                AgentsUtilities = [];

                foreach (var agent in Dispute.Agents)
                {
                    List<AgentUtility> agentUtilities = Dispute.Goods
                        .Select(good => Dispute.AgentUtilities.
                            FirstOrDefault(u => u.AgentId == agent.AgentId && u.GoodId == good.GoodId)
                        ).ToList();

                    AgentsUtilities.Add(agentUtilities);
                }

                RestrictedAssignments = [];
                foreach (RestrictedAssignment ra in Dispute.RestrictedAssignments)
                {
                    RestrictedAssignments.Add(ra);
                }

                RestrictedGoods = Dispute
                    .RestrictedAssignments.Select(ra => ra.Good)
                    .Distinct()
                    .ToList();
                
                int variablesNumber =
                    (Dispute.Goods.Count + RestrictedGoods.Count) * Dispute.Agents.Count;
                int constraintsNumber =
                    variablesNumber
                    + 2 * (Dispute.Goods.Count + RestrictedGoods.Count)
                    + 2 * RestrictedAssignments.Count;

                double[] variables = new double[variablesNumber];

                Cobyla optimizer = new Cobyla(
                    variablesNumber,
                    constraintsNumber,
                    calcfc: Objective
                );
                ResultNash = optimizer.FindMinimum(variables);

                int index = 0;
                for (int i = 0; i < Dispute.Agents.Count; i++)
                {
                    for (int j = 0; j < Dispute.Goods.Count + RestrictedGoods.Count; j++)
                    {
                        Debug.WriteLine(
                            "x"
                                + (i + 1).ToString()
                                + (j + 1).ToString()
                                + ": "
                                + Math.Abs(Math.Round(ResultNash.X[index], 2))
                        );
                        index++;
                    }
                }

                int agentId = Context.Agents
                    .FirstOrDefault(a => a.DisputeId == id && a.CreaUserId == UserManager.GetUserId(User))
                    .AgentId;
                
                CurrentAgentUtilities = Dispute.AgentUtilities
                    .Where(d => d.AgentId == agentId)
                    .ToList();
            }
        }

        private void Objective(
            int variablesNumber,
            int constraintsNumber,
            double[] x,
            out double function,
            double[] constraints
        )
        {
            function = -1;
            int i,
                j,
                index = 0;
            for (i = 0; i < Dispute.Agents.Count; i++)
            {
                Dispute.Agents[i].Dispute = Dispute;
                double temp = 0;
                for (j = 0; j < Dispute.Goods.Count; j++)
                {
                    temp += x[index] * (double)AgentsUtilities[i][j].Utility;
                    index++;
                }
                for (j = 0; j < RestrictedGoods.Count; j++)
                {
                    temp += x[index] * (double)RestrictedGoods[j].EstimatedValue;
                    index++;
                }
                double weight = (double)Dispute.Agents[i].ShareOfEntitlement / 100;
                function *= Math.Pow(temp, weight);
            }

            int constraintIndex = -1;
            for (i = 0; i < variablesNumber; i++)
            {
                constraintIndex++;
                constraints[constraintIndex] = x[i];
            }

            for (i = 0; i < Dispute.Goods.Count + RestrictedGoods.Count; i++)
            {
                constraintIndex++;
                constraints[constraintIndex] = -1;
                for (j = 0; j < Dispute.Agents.Count; j++)
                {
                    constraints[constraintIndex] += x[
                        i + j * (Dispute.Goods.Count + RestrictedGoods.Count)
                    ];
                }
            }

            for (i = 0; i < Dispute.Goods.Count + RestrictedGoods.Count; i++)
            {
                constraintIndex++;
                constraints[constraintIndex] = 1;
                for (j = 0; j < Dispute.Agents.Count; j++)
                {
                    constraints[constraintIndex] -= x[
                        i + j * (Dispute.Goods.Count + RestrictedGoods.Count)
                    ];
                }
            }

            for (i = 0; i < RestrictedAssignments.Count; i++)
            {
                constraintIndex++;
                double assignedShare = (double)RestrictedAssignments[i].ShareOfEntitlement / 100;
                int assignedGoodId = RestrictedAssignments[i].GoodId - 1;
                int recipientAgentId = RestrictedAssignments[i].AgentId - 1;

                constraints[constraintIndex] =
                    x[
                        assignedGoodId
                            + recipientAgentId * (Dispute.Goods.Count + RestrictedGoods.Count)
                    ] - assignedShare;
            }

            for (i = 0; i < RestrictedAssignments.Count; i++)
            {
                constraintIndex++;
                double assignedShare = (double)RestrictedAssignments[i].ShareOfEntitlement / 100;
                int assignedGoodId = RestrictedAssignments[i].GoodId - 1;
                int recipientAgentId = RestrictedAssignments[i].AgentId - 1;

                constraints[constraintIndex] =
                    -x[
                        assignedGoodId
                            + recipientAgentId * (Dispute.Goods.Count + RestrictedGoods.Count)
                    ] + assignedShare;
            }
        }
    }
}
