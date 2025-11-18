using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CreaProject.Migrations
{
    /// <inheritdoc />
    public partial class DisputeBlockId : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "BlockId",
                table: "Disputes",
                type: "nvarchar(max)",
                nullable: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "BlockId",
                table: "Disputes");
        }
    }
}
