using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace CreaProject.Migrations
{
    /// <inheritdoc />
    public partial class CheckPendingChanges : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_Agents_Email_DisputeId",
                table: "Agents");

            migrationBuilder.AlterColumn<string>(
                name: "Email",
                table: "Agents",
                type: "nvarchar(450)",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "nvarchar(450)");

            migrationBuilder.CreateIndex(
                name: "IX_Agents_Email_DisputeId",
                table: "Agents",
                columns: new[] { "Email", "DisputeId" },
                unique: true,
                filter: "[Email] IS NOT NULL");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_Agents_Email_DisputeId",
                table: "Agents");

            migrationBuilder.AlterColumn<string>(
                name: "Email",
                table: "Agents",
                type: "nvarchar(450)",
                nullable: false,
                defaultValue: "",
                oldClrType: typeof(string),
                oldType: "nvarchar(450)",
                oldNullable: true);

            migrationBuilder.CreateIndex(
                name: "IX_Agents_Email_DisputeId",
                table: "Agents",
                columns: new[] { "Email", "DisputeId" },
                unique: true);
        }
    }
}
