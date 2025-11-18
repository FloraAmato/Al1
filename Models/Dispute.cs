using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;

namespace CreaProject.Models
{
    public class Dispute
    {
        public int DisputeId { get; set; }

        // user ID from AspNetUser table.
        public string OwnerId { get; set; }

        public string Name { get; set; }

        public string BlockId { get; set; }

        public DisputeStatus Status { get; set; }

        public DisputeResolutionMethod ResolutionMethod { get; set; }

        private const double BoundPercentageDefault = 25;
        private double? _boundPercentage;

        public double? BoundsPercentage
        {
            get => _boundPercentage * 100;
            set
            {
                if (value != null)
                    _boundPercentage = (double)value / 100;
                else
                    _boundPercentage = BoundPercentageDefault / 100;
            }
        }

        private const double RatingWeightDefault = 1.1;
        public double _ratingWeight;
        public double? RatingWeight
        {
            get => (Math.Abs(_ratingWeight - 1)) * 100;
            set
            {
                if (value != null)
                    _ratingWeight = 1 + (double)value / 100;
                else
                    _ratingWeight = RatingWeightDefault;
            }
        }

        public List<Agent> Agents { get; set; }
        public List<Good> Goods { get; set; }
        public List<AgentUtility> AgentUtilities { get; set; }
        public IEnumerable<RestrictedAssignment> RestrictedAssignments { get; set; }

        public virtual string AgentsNameList
        {
            get
            {
                return Agents != null ? string.Join(", ", Agents.Select(g => g.Name).ToList()) : "";
            }
        }

        public double AgentsShareOfEntitlement
        {
            get
            {
                var shared = 1.0;
                var numAgents = 1;
                if (Agents != null)
                {
                    numAgents = Agents.Count;
                    foreach (var agent in Agents.Where(agent => agent._shareOfEntitlement != 0))
                    {
                        shared = shared - agent._shareOfEntitlement;
                        numAgents--;
                    }
                }
                if (shared >= 0)
                    return shared / numAgents;
                else
                    return 0.0;
            }
        }

        public virtual string GoodsNameList
        {
            get
            {
                return Goods != null ? string.Join(", ", Goods.Select(g => g.Name).ToList()) : "";
            }
        }

        public double DisputeBudget
        {
            get
            {
                if (Goods == null) return 0;
                var goodsValueSum = (double)Goods.Sum(g => g.EstimatedValue);
                return goodsValueSum + (goodsValueSum * (double)_boundPercentage);

            }
        }

        [Display(Name = "Creation date")]
        [DisplayFormat(DataFormatString = "{0:dd MMMM yyyy}")]
        public DateTime? CreatedAt { get; set; }

        [Display(Name = "Update date")]
        [DisplayFormat(DataFormatString = "{0:dd MMMM yyyy}")]
        public DateTime? UpdatedAt { get; set; }
    }

    public enum DisputeResolutionMethod
    {
        Ratings,
        Bids
    }

    public enum DisputeStatus
    {
        [Display(Name = "Procedure initialization")]
        SettingUp,

        [Display(Name = "Agent's preferences")]
        Bidding,

        [Display(Name = "Solution evaluation")]
        Finalizing,

        [Display(Name = "Agreement")]
        Finalized,
        
        [Display(Name = "Rejected")]
        Rejected
    }
}
