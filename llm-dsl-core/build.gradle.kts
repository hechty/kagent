import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    kotlin("jvm")
    kotlin("plugin.serialization")
    `java-library`
}

group = "com.llmservice"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    // Kotlin标准库
    implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
    
    // Ktor客户端依赖
    implementation("io.ktor:ktor-client-core:2.3.5")
    implementation("io.ktor:ktor-client-cio:2.3.5")
    implementation("io.ktor:ktor-client-content-negotiation:2.3.5")
    implementation("io.ktor:ktor-client-logging:2.3.5")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.5")
    
    // 日志依赖
    implementation("ch.qos.logback:logback-classic:1.4.11")
    
    // 测试依赖
    testImplementation("org.jetbrains.kotlin:kotlin-test")
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")
    testImplementation("org.junit.jupiter:junit-jupiter-engine:5.10.0")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
}

tasks.test {
    useJUnitPlatform()
}

tasks.withType<KotlinCompile> {
    kotlinOptions.jvmTarget = "21"
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}

// DSL测试任务
tasks.register<JavaExec>("runDSLTest") {
    group = "application"
    description = "Run DSL quick test"
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.llmservice.dsl.DSLQuickTestKt")
    
    doFirst {
        println("Starting DSL test without web server...")
    }
}

tasks.register<JavaExec>("runDSLDemo") {
    group = "application"
    description = "Run DSL quick demo"
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.llmservice.dsl.DSLQuickDemoKt")
    
    doFirst {
        println("Starting DSL demo...")
    }
}

tasks.register<JavaExec>("runStandaloneDSLTest") {
    group = "application"
    description = "Run standalone DSL test"
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("com.llmservice.dsl.StandaloneDSLTestKt")
    
    doFirst {
        println("Starting standalone DSL test...")
    }
}