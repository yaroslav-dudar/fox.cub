import sbt.Package._

name:= "Fox.Cub"

version := "0.0.1"

scalaVersion := "2.12.6"

libraryDependencies ++= Seq(
    "io.vertx" %% "vertx-lang-scala" % "3.5.4",
    "io.vertx" %% "vertx-web-scala" % "3.5.4",
    "io.vertx" %% "vertx-config-scala" % "3.5.4",
    "io.vertx" %% "vertx-mongo-client-scala" % "3.5.4",
    "io.vertx" % "vertx-web-api-contract" % "3.5.4",

    "org.deeplearning4j" % "deeplearning4j-core" % "1.0.0-beta3",
    "org.nd4j" % "nd4j-native-platform" % "1.0.0-beta3"
)

packageOptions += ManifestAttributes(
    ("Main-Verticle", "scala:fox.cub.HttpVerticle")
)

resolvers ++= Seq(
  "Typesafe" at "http://repo.typesafe.com/typesafe/releases/",
  "Java.net Maven2 Repository" at "http://download.java.net/maven/2/"
)

fork := true
javaOptions := Seq("-Dvertx-config-path=./config/config.json")
