using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CreaProject.Migrations
{
    /// <inheritdoc />
    public partial class AgentValidation : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<bool>(
                name: "Validated",
                table: "Agents",
                type: "bit",
                nullable: false,
                defaultValue: false);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn( 
                name: "Validated",
                table: "Agents");
        }
    }
}
