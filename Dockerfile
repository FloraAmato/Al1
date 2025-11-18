FROM mcr.microsoft.com/dotnet/sdk:8.0 AS publish
WORKDIR /src

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

COPY . .

RUN dotnet restore "./CreaProject.csproj"

WORKDIR /src
RUN npm install
RUN npm run css:build

RUN dotnet publish "./CreaProject.csproj" -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app
EXPOSE 8080
COPY --from=publish /app .
ENTRYPOINT ["dotnet", "CreaProject.dll"]