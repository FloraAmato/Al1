using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using CreaProject.Areas.Identity.Data;

namespace CreaProject.Models
{
    public class Agent
    {
        public int AgentId { get; set; }


        [ForeignKey("CreaUser")] public string CreaUserId { get; set; }

        public CreaUser CreaUser { get; set; }

        [Required]
        [EmailAddress(ErrorMessage = "Invalid Email Address")]
        public string Email { get; set; }

        public double _shareOfEntitlement;
        public double? ShareOfEntitlement
        {
            get 
            {
                if (_shareOfEntitlement != 0)
                    return _shareOfEntitlement * 100;
                if (Dispute!=null)
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
        public IEnumerable<RestrictedAssignment> RestrictedAssignments { get; set; }

        public virtual string Name
        {
            get
            {
                if (CreaUser != null)
                    return string.Concat(CreaUser.Surname, " ", CreaUser.Name);
                return "(No name)";
            }
        }
    }
}