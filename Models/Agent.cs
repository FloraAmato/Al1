using CreaProject.Areas.Identity.Data;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CreaProject.Models
{
    public class Agent
    {
        public int AgentId { get; set; }

        [ForeignKey("CreaUser")]
        public string CreaUserId { get; set; }

        public CreaUser CreaUser { get; set; }

        [EmailAddress(ErrorMessage = "Invalid Email Address")]
        public string Email { get; set; }

        public double _shareOfEntitlement;

        [Display(Name = "Share of Entitlement")]
        public double? ShareOfEntitlement
        {
            get
            {
                if (_shareOfEntitlement != 0)
                    return _shareOfEntitlement * 100;
                if (Dispute != null)
                    return Dispute.AgentsShareOfEntitlement * 100;
                return 0;
            }
            set
            {
                if (value != null)
                    _shareOfEntitlement = (double)value / 100;
            }
        }

        public int DisputeId { get; set; }
        public Dispute Dispute { get; set; }

        public IEnumerable<AgentUtility> AgentUtilities;
        
        private string fullName;

        public IEnumerable<RestrictedAssignment> RestrictedAssignments { get; set; }

        public virtual string Name => CreaUser != null ? string.Concat(CreaUser.Surname, " ", CreaUser.Name) : null;

        public ValidatedSteps Validated { get; set; }
    }
    
    public enum ValidatedSteps
    {
        None,
        Setup,
        Bids,
        Agreement,
        Disagreement
    }
}
