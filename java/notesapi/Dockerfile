# ---- Stage 1: Build ----
FROM maven:3.9.6-eclipse-temurin-21 AS builder

# Set the working directory inside the container
WORKDIR /app

COPY pom.xml .

# Download all dependencies
RUN mvn -q dependency:go-offline

COPY src ./src

# Compile the app and create app.jar
RUN mvn -q package -DskipTests

# ---- Stage 2: Runtime ----
FROM eclipse-temurin:21-jre AS runtime
WORKDIR /app

# Copy JAR built in Stage 1 into Stage 2
COPY --from=builder /app/target/*.jar app.jar

EXPOSE 8080

# Command that runs the app
ENTRYPOINT ["java", "-jar", "app.jar"]
