import sbt.Package._

name:= "Fox.Cub"

version := "0.0.1"

scalaVersion := "2.12.12"

libraryDependencies ++= Seq(
    "io.vertx" %% "vertx-lang-scala" % "3.5.4",
    "io.vertx" %% "vertx-web-scala" % "3.5.4",
    "io.vertx" %% "vertx-config-scala" % "3.5.4",
    "io.vertx" %% "vertx-auth-jwt-scala" % "3.5.4",
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
javaOptions := Seq("-Dvertx-config-path=./../config/config.json")

mainClass in assembly := Some("fox.cub.FoxCub")
// name of the resulting jar file
assemblyOutputPath in assembly := file("./FoxCub.jar")

assemblyMergeStrategy in assembly := {
    case PathList(ps @ _*) if ps.mkString("/") contains "libjniopencv_"     => MergeStrategy.discard
    case PathList(ps @ _*) if ps.mkString("/") contains "libopencv_"     => MergeStrategy.discard
    case PathList(ps @ _*) if ps.mkString("/") contains "macosx-x86_64"     => MergeStrategy.discard
    case PathList(ps @ _*) if ps.mkString("/") contains "windows-x86"     => MergeStrategy.discard
    case PathList(ps @ _*) if ps.mkString("/") contains "macosx-x86_64"     => MergeStrategy.discard
    case PathList(ps @ _*) if ps.mkString("/") contains "ios-x86_64"     => MergeStrategy.discard
    case PathList(ps @ _*) if ps.mkString("/") contains "ios-arm64"     => MergeStrategy.discard

    case PathList("META-INF", "io.netty.versions.properties")     => MergeStrategy.last
    case PathList(ps @ _*) if ps.last endsWith "Nd4jBase64.class" => MergeStrategy.last
    case PathList(ps @_ *) if ps.last endsWith "codegen.json"     => MergeStrategy.last
    case PathList(ps @ _*) if ps.last endsWith "jnijavacpp.o"     => MergeStrategy.last
    case x =>
        val oldStrategy = (assemblyMergeStrategy in assembly).value
        oldStrategy(x)
}
