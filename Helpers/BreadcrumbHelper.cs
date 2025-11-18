using CreaProject.Models;
using System.Collections.Generic;

namespace CreaProject.Helpers
{
    public static class BreadcrumbHelper
    {
        public static List<BreadcrumbStep> GetBreadcrumbSteps(DisputeStatus status, int disputeId)
        {
            var steps = new List<BreadcrumbStep>
            {
                new() { Title = "Procedure initialization", State = BreadcrumbState.Inactive, Url = $"/Disputes/Create/{disputeId}" },
                new() { Title = "Agent's preferences", State = BreadcrumbState.Inactive, Url = $"/Disputes/Bids/{disputeId}" },
                new() { Title = "Solution evaluation", State = BreadcrumbState.Inactive, Url = $"/Disputes/Solution/{disputeId}" },
                new() { Title = "Agreement", State = BreadcrumbState.Inactive, Url = $"/Disputes/Solution/{disputeId}" }
            };

            switch (status)
            {
                case DisputeStatus.SettingUp:
                    steps[0].State = BreadcrumbState.Ongoing;
                    break;
                case DisputeStatus.Bidding:
                    steps[0].State = BreadcrumbState.Completed;
                    steps[1].State = BreadcrumbState.Ongoing;
                    break;
                case DisputeStatus.Finalizing:
                    steps[0].State = BreadcrumbState.Completed;
                    steps[1].State = BreadcrumbState.Completed;
                    steps[2].State = BreadcrumbState.Ongoing;
                    break;
                case DisputeStatus.Rejected:
                case DisputeStatus.Finalized:
                    steps[0].State = BreadcrumbState.Completed;
                    steps[1].State = BreadcrumbState.Completed;
                    steps[2].State = BreadcrumbState.Completed;
                    steps[3].State = BreadcrumbState.Completed;
                    break;
            }

            return steps;
        }
    }
}
