using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CreaProject.Models
{
    public class Bid : AgentUtility
    {
        [Required]
        [DataType(DataType.Currency)]
        [Column(TypeName = "money")]
        public decimal BidValue { get; set; }

        public decimal LowerBound
        {
            get
            {
                if (Good != null && Dispute!=null)
                    return Good.EstimatedValue - Good.EstimatedValue * (decimal)Dispute.BoundsPercentage / 100;
                return 0M;
            }
        }

        public decimal UpperBound
        {
            get
            {
                if (Good != null && Dispute != null)
                    return Good.EstimatedValue + Good.EstimatedValue * (decimal)Dispute.BoundsPercentage / 100;
                return 0M;
            }
        }

        public override decimal Utility => BidValue;
    }
}