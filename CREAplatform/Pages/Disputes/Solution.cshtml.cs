using System;
using Google.OrTools.LinearSolver;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using CreaProject.Areas.Identity.Data;
using CreaProject.Authorization;
using CreaProject.Data;
using CreaProject.Models;
using Cureos.Numerics.Optimizers;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Constraint = Google.OrTools.LinearSolver.Constraint;

namespace CreaProject.Pages.Disputes
{
    public class SolutionModel : DisputeBasePageModel
    {
        public SolutionModel(
            ApplicationDbContext context,
            IAuthorizationService authorizationService,
            UserManager<CreaUser> userManager)
            : base(context, authorizationService, userManager)
        {
        }

        [BindProperty] public List<List<Variable>> ProblemVars { get; private set;}
        [BindProperty] public OptimizationSummary ResultNash { get; private set;}
        [BindProperty] public List<AgentUtility> CurrentAgentUtilities { get; private set; }

        private List<List<AgentUtility>> AgentsUtilities { get; set; }
        private List<RestrictedAssignment> RestrictedAssignments { get; set; }
        private List<Good> RestrictedGoods { get; set; }

        public async Task<IActionResult> OnGetAsync(int id)
        {
            Dispute = await Context.Disputes
                .AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (Dispute == null) return NotFound();
            
            if (!Dispute.Status.Equals(DisputeStatus.Finalizing))
                return new ForbidResult();

            var isMediator = await AuthorizationService.AuthorizeAsync(User, Dispute,
                DisputeOperations.Update);
            var isAgent = await AuthorizationService.AuthorizeAsync(User, Dispute,
                DisputeOperations.Bid);

            if (!isMediator.Succeeded && !isAgent.Succeeded)
                return new ChallengeResult();


            if (Dispute.ResolutionMethod.Equals(DisputeResolutionMethod.Ratings))
                SolveRating(id);
            else
            {
                SolveBids(id);
                
            }


            return Page();
        }

        public async Task<IActionResult> OnPostAcceptAsync(int id)
        {
            if (!ModelState.IsValid) return RedirectToPage("Edit", new { id });

            // Fetch Dispute from DB to get OwnerID.
            var dispute = await Context
                .Disputes.AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (dispute == null) return NotFound();

            var isAuthorized = await AuthorizationService.AuthorizeAsync(
                User, dispute,
                DisputeOperations.Update);
            if (!isAuthorized.Succeeded) return new ChallengeResult();

            return RedirectToPage("Edit", new {id});
        }


        public async Task<IActionResult> OnPostRejectAsync(int id)
        {
            if (!ModelState.IsValid) return RedirectToPage("Edit", new { id });

            // Fetch Dispute from DB to get OwnerID.
            var dispute = await Context
                .Disputes.Include(d => d.Agents).Include(d => d.Goods).AsNoTracking()
                .FirstOrDefaultAsync(m => m.DisputeId == id);

            if (dispute == null) return NotFound();

            var isAuthorized = await AuthorizationService.AuthorizeAsync(
                User, dispute,
                DisputeOperations.Update);
            if (!isAuthorized.Succeeded) return new ChallengeResult();

            


            return RedirectToPage("Edit", new {id});
        }


        private void SolveRating(int id)
        {
            Dispute = Context.Disputes
                .Include(d => d.Agents)
                .Include(d => d.Goods)
                .Include(d => d.AgentUtilities)
                .ThenInclude(u => u.Good)
                .Include(d => d.RestrictedAssignments)
                .ThenInclude(u=>u.Good)
                .AsNoTracking()
                .FirstOrDefault(m => m.DisputeId == id);

            if (Dispute != null)
            {
                Dispute.Agents = Context.Agents.Include(a => a.CreaUser).Where(a => a.DisputeId == id).ToList();


                List<List<AgentUtility>> agentsUtilities = new List<List<AgentUtility>>();


                foreach (var agent in Dispute.Agents)
                {
                    var agentUtilities = new List<AgentUtility>();
                    foreach (var good in Dispute.Goods)
                    {
                        agentUtilities.Add(Dispute.AgentUtilities.FirstOrDefault(u =>
                            u.AgentId == agent.AgentId && u.GoodId == good.GoodId));
                    }

                    agentsUtilities.Add(agentUtilities);
                }


                List<RestrictedAssignment> restrictedAssignments = new List<RestrictedAssignment>();
                foreach (var ra in Dispute.RestrictedAssignments)
                {
                    restrictedAssignments.Add(ra);
                }

                var restrictedGoods = Dispute.RestrictedAssignments.Select(ra => ra.Good).Distinct().ToList();

                int totalGoodsCount = Dispute.Goods.Count + restrictedGoods.Count;

                Solver solver = Solver.CreateSolver("SimpleMipProgram", "CBC_MIXED_INTEGER_PROGRAMMING");

                //istanziamo la matrice delle variabili soluzione

                int i, j;
                ProblemVars = new List<List<Variable>>();
                for (i = 0; i < Dispute.Agents.Count; i++)
                {
                    var zRow = new List<Variable>();
                    for (j = 0; j < Dispute.Goods.Count; j++)
                    {
                        if (Dispute.Goods[j].Indivisible)
                            zRow.Add(solver.MakeIntVar(0.0, 1.0, "z" + (i + 1) + (j + 1)));
                        else
                            zRow.Add(solver.MakeNumVar(0.0, 1.0, "z" + (i + 1) + (j + 1)));
                    }

                    for (j = 0; j < restrictedGoods.Count; j++)
                        zRow.Add(solver.MakeNumVar(0.0, 1.0,
                            "z" + (i + 1) + (j + Dispute.Goods.Count + 1)));

                    ProblemVars.Add(zRow);
                }

                //istanziamo la variabile di comodo
                Variable t = solver.MakeNumVar(0.0, double.PositiveInfinity, "t");


                //ricaviamo i coefficienti delle z nell'espressione, cioè u/(w*somma di u)
                var coefficients = new List<List<decimal>>();
                for (i = 0; i < Dispute.Agents.Count; i++)
                {

                    var coefficientsRow = new List<decimal>();

                    Dispute.Agents[i].Dispute = Dispute;
                    //calcoliamo il peso dell'agente
                    decimal weight = (decimal)Dispute.Agents[i].ShareOfEntitlement / 100;

                    //calcoliamo la somma delle utilità al denominatore
                    decimal goodsUtilitiesSum = 0;

                    //sommiamo prima tutte le offerte dell'agente
                    for (j = 0; j < Dispute.Goods.Count; j++)
                        goodsUtilitiesSum += agentsUtilities[i][j].Utility;

                    //sommiamo poi i valori di mercato degli eventuali beni con restrizioni
                    for (j = 0; j < restrictedGoods.Count; j++)
                        goodsUtilitiesSum += restrictedGoods[j].EstimatedValue;

                    //calcoliamo i coefficienti
                    for (j = 0; j < totalGoodsCount; j++)
                    {
                        decimal temp;

                        //per i beni non preassegnati usiamo le offerte come utilità
                        if (j < Dispute.Goods.Count)
                        {
                            temp = agentsUtilities[i][j].Utility / (goodsUtilitiesSum * weight);
                        }
                        else //per i beni con restrizioni usiamo invece il valore di mercato
                        {
                            temp = restrictedGoods[j - Dispute.Goods.Count].EstimatedValue /
                                   (goodsUtilitiesSum * weight);
                        }

                        coefficientsRow.Add(temp);
                    }

                    coefficients.Add(coefficientsRow);
                }


                //creiamo i vincoli
                List<Constraint> constraints = new List<Constraint>();
                //per ogni bene la somma sugli agenti delle z deve essere uguale a 1
                for (j = 0; j < totalGoodsCount; j++)
                {
                    constraints.Add(solver.MakeConstraint(1.0, 1.0));
                    for (i = 0; i < Dispute.Agents.Count; i++)
                    {
                        constraints[j].SetCoefficient(ProblemVars[i][j], 1);
                    }
                }

                //per ogni agente la somma sui beni di (coefficiente*z - t) deve essere maggiore di 0
                for (i = 0; i < Dispute.Agents.Count; i++)
                {
                    constraints.Add(solver.MakeConstraint(0.0, double.PositiveInfinity));

                    for (j = 0; j < totalGoodsCount; j++)
                    {
                        constraints[i + totalGoodsCount]
                            .SetCoefficient(ProblemVars[i][j], (double) coefficients[i][j]);
                    }

                    constraints[i + totalGoodsCount].SetCoefficient(t, -1);
                }

                //per i beni con restrizioni vincoliamo la soluzione al valore prestabilito
                for (i = 0; i < restrictedAssignments.Count; i++)
                {
                    double assignedShare = (double) restrictedAssignments[i].ShareOfEntitlement / 100;
                    int assignedGoodId = restrictedAssignments[i].GoodId - 1;
                    int recipientAgentId = restrictedAssignments[i].AgentId - 1;

                    constraints.Add(solver.MakeConstraint(assignedShare, assignedShare));
                    constraints[i + totalGoodsCount + Dispute.Agents.Count]
                        .SetCoefficient(ProblemVars[recipientAgentId][assignedGoodId], 1);
                }


                Objective objective = solver.Objective(); //istanziamo l'obiettivo
                objective.SetCoefficient(t, 1); //la funzione obiettivo è t
                objective.SetMaximization(); //lo scopo è massimizzare t

                solver.Solve(); //risolviamo

//                Debug.WriteLine("Solution:"); //stampiamo la matrice soluzione
//                Debug.WriteLine("Objective value = " + solver.Objective().Value());
//                for (i = 0; i < Dispute.Agents.Count; i++)
//                for (j = 0; j < totalGoodsCount; j++)
//                    Debug.WriteLine("z" + (i + 1).ToString() + (j + 1).ToString() + " = " +
//                                    Decimal.Round((decimal) ProblemVars[i][j].SolutionValue(), 2));
//                Debug.WriteLine("t = " + t.SolutionValue());
                
            }
        }
        
        private void SolveBids(int id)
        {
            Dispute = Context.Disputes
                .Include(d => d.Agents)
                .Include(d => d.Goods)
                .Include(d => d.AgentUtilities)
                .ThenInclude(u => u.Good)
                .Include(d => d.RestrictedAssignments)
                .ThenInclude(u=>u.Good)
                .AsNoTracking()
                .FirstOrDefault(m => m.DisputeId == id);

            if (Dispute != null)
            {
                Dispute.Agents = Context.Agents.Include(a => a.CreaUser).Where(a => a.DisputeId == id).ToList();


                AgentsUtilities = new List<List<AgentUtility>>();


                foreach (var agent in Dispute.Agents)
                {
                    var agentUtilities = new List<AgentUtility>();
                    foreach (var good in Dispute.Goods)
                    {
                        agentUtilities.Add(Dispute.AgentUtilities.FirstOrDefault(u =>
                            u.AgentId == agent.AgentId && u.GoodId == good.GoodId));
                    }

                    AgentsUtilities.Add(agentUtilities);
                }


                RestrictedAssignments = new List<RestrictedAssignment>();
                foreach (var ra in Dispute.RestrictedAssignments)
                {
                    RestrictedAssignments.Add(ra);
                }

                RestrictedGoods = Dispute.RestrictedAssignments.Select(ra => ra.Good).Distinct().ToList();

                //int totalGoodsCount = Dispute.Goods.Count + RestrictedGoods.Count;

                int variablesNumber = (Dispute.Goods.Count + RestrictedGoods.Count) * Dispute.Agents.Count;
                int constraintsNumber = variablesNumber + 2 * (Dispute.Goods.Count + RestrictedGoods.Count) +
                                        2 * RestrictedAssignments.Count;

                double[] variables = new double[variablesNumber];

                Cobyla optimizer = new Cobyla(variablesNumber, constraintsNumber, calcfc: Objective);
                ResultNash = optimizer.FindMinimum(variables);

                int index = 0;
                for (int i = 0; i < Dispute.Agents.Count; i++) //stampa della soluzione
                {
                    for (int j = 0; j < Dispute.Goods.Count + RestrictedGoods.Count; j++)
                    {
                        Debug.WriteLine("x" + (i + 1).ToString() + (j + 1).ToString() + ": " +
                                          Math.Abs(Math.Round(ResultNash.X[index], 2)));
                        index++;
                    }
                }

                var agentId = Context.Agents.FirstOrDefault(a => a.DisputeId == id && a.CreaUserId == UserManager.GetUserId(User)).AgentId;
                CurrentAgentUtilities = Dispute.AgentUtilities.Where(d => d.AgentId == agentId).ToList();

            }
            
        }

        private void Objective(int variablesNumber, int constraintsNumber, double[] x, out double function, double[] constraints)
        {

            function = -1; //poichè la libreria è solo per minimizzazioni cambiamo il segno della funzione obiettivo
            int i, j, index = 0;
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
            for (i = 0; i < variablesNumber; i++) //tutte le soluzioni devono essere maggiori o uguali di 0
            {
                constraintIndex++;
                constraints[constraintIndex] = x[i];
            }

            //la somma delle x per ogni bene deve essere uguale a 1, ovvero contemporaneamente >=1 e <=1
            for (i = 0; i < Dispute.Goods.Count + RestrictedGoods.Count; i++) // >=1
            {

                constraintIndex++;
                constraints[constraintIndex] = -1;
                for (j = 0; j < Dispute.Agents.Count; j++)
                {
                    constraints[constraintIndex] += x[i + j * (Dispute.Goods.Count + RestrictedGoods.Count)];
                }

            }

            for (i = 0; i < Dispute.Goods.Count + RestrictedGoods.Count; i++) // <=1
            {

                constraintIndex++;
                constraints[constraintIndex] = 1;
                for (j = 0; j < Dispute.Agents.Count; j++)
                {
                    constraints[constraintIndex] -= x[i + j * (Dispute.Goods.Count + RestrictedGoods.Count)];
                }

            }

            for (i = 0; i < RestrictedAssignments.Count; i++) //for each restricted assignment we bond the solution to its predetermined value
            {

                constraintIndex++;
                double assignedShare = (double)RestrictedAssignments[i].ShareOfEntitlement / 100;
                int assignedGoodId = RestrictedAssignments[i].GoodId - 1;
                int recipientAgentId = RestrictedAssignments[i].AgentId - 1;

                constraints[constraintIndex] = x[assignedGoodId + recipientAgentId * (Dispute.Goods.Count + RestrictedGoods.Count)] - assignedShare;

            }

            for (i = 0; i < RestrictedAssignments.Count; i++) //for each restricted assignment we bond the solution to its predetermined value
            {

                constraintIndex++;
                double assignedShare = (double)RestrictedAssignments[i].ShareOfEntitlement / 100;
                int assignedGoodId = RestrictedAssignments[i].GoodId - 1;
                int recipientAgentId = RestrictedAssignments[i].AgentId - 1;

                constraints[constraintIndex] = - x[assignedGoodId + recipientAgentId * (Dispute.Goods.Count + RestrictedGoods.Count)] + assignedShare;

            }
        }
        
        
    }
}