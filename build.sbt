import sbt.Package._

name:= "Fox.Cub.API"

version := "0.0.1"

scalaVersion := "2.12.6"

libraryDependencies ++= Seq(
    "io.vertx" %% "vertx-lang-scala" % "3.5.3",
    "io.vertx" %% "vertx-web-scala" % "3.5.3",
    "io.vertx" %% "vertx-mongo-client-scala" % "3.5.3"
)

packageOptions += ManifestAttributes(
    ("Main-Verticle", "scala:fox.cub.HttpVerticle")
)
