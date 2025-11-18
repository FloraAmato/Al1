using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CreaProject.Models
{
    public class Good
    {
        public int GoodId { get; set; }

        [Required] public string Name { get; set; }

        [Required]
        [DataType(DataType.Currency)]
        [Column(TypeName = "money")]
        public decimal EstimatedValue { get; set; }

        public bool Indivisible { get; set; }

        public IEnumerable<AgentUtility> AgentUtilities { get; set; }
        
        public IEnumerable<RestrictedAssignment> RestrictedAssignments { get; set; }

        [Required] public int DisputeId { get; set; }

        public Dispute Dispute { get; set; }
    }
}