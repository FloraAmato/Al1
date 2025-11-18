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

        [Required]
        public string Name { get; set; }

        public DisputeStatus Status { get; set; }

        [Required]
        public DisputeResolutionMethod ResolutionMethod { get; set; }

        private const double boundPercentageDefalut = 25;
        private double? _boundPercentage;

        public double? BoundsPercentage {
            get { return _boundPercentage * 100; }
            set
            {
                if (value != null)
                    _boundPercentage = (double)value / 100;
                else
                    _boundPercentage = boundPercentageDefalut / 100;
            }
        }

        private const double ratingWeightDefault = 1.1;
        public double _ratingWeight;
        public double? RatingWeight
        {
            get { return (1-_ratingWeight)*100; }
            set
            {
                if (value != null)
                    _ratingWeight = 1 + (double)value / 100;
                else
                    _ratingWeight = ratingWeightDefault;
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
                if (Agents != null)
                    return string.Join(", ", Agents.Select(g => g.Name).ToList());
                return "";
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
                    foreach (var agent in Agents)
                    {
                        if (agent._shareOfEntitlement != 0)
                        {
                            shared = shared - agent._shareOfEntitlement;
                            numAgents--;
                        }
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
                if (Goods != null)
                    return string.Join(", ", Goods.Select(g => g.Name).ToList());
                return "";
            }
        }

        public double DisputeBudget
        {
            get
            {
                if (Goods != null)
                {
                    var goodsValueSum = (double)Goods.Sum(g => g.EstimatedValue);
                    return goodsValueSum + (goodsValueSum * (double)_boundPercentage);
                }
                   
                return 0;
            }
        }
    }

    public enum DisputeResolutionMethod
    {
        Ratings,
        Bids        
    }

    public enum DisputeStatus
    {
        [Display(Name = "Initialization")] SettingUp,
        [Display(Name = "User preferences")] Bidding,
        [Display(Name = "Evaluating solution")] Finalizing
    }
}