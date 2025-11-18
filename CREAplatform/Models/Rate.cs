using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace CreaProject.Models
{
    public class Rate : AgentUtility
    {
        
        private const int NumberOfStars = 5;

        [Required] [Range(1, NumberOfStars)] public int RateValue { get; set; }

        public override decimal Utility
        {
            get
            {
                if (Good != null)
                    return Convert.ToDecimal(Math.Pow((double)Dispute._ratingWeight, RateValue - 3)) * Good.EstimatedValue;

                return 0;
            }
        }
    }
}