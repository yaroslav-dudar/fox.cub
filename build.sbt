import sbt.Package._

name:= "Fox.Cub"

version := "0.0.1"

scalaVersion := "2.12.6"

libraryDependencies ++= Seq(
    "io.vertx" %% "vertx-lang-scala" % "3.5.3",
    "io.vertx" %% "vertx-web-scala" % "3.5.3",
    "io.vertx" %% "vertx-config-scala" % "3.5.3",
    "io.vertx" %% "vertx-mongo-client-scala" % "3.5.3"
)

packageOptions += ManifestAttributes(
    ("Main-Verticle", "scala:fox.cub.HttpVerticle")
)

fork := true
javaOptions := Seq("-Dvertx-config-path=./config/config.json")
