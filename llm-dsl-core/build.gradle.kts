plugins {
    kotlin("jvm")
    kotlin("plugin.serialization")
    `java-library`
}

dependencies {
    // Ktor客户端依赖 - DSL核心模块特有
    implementation("io.ktor:ktor-client-core:${property("ktorVersion")}")
    implementation("io.ktor:ktor-client-cio:${property("ktorVersion")}")
    implementation("io.ktor:ktor-client-content-negotiation:${property("ktorVersion")}")
    implementation("io.ktor:ktor-client-logging:${property("ktorVersion")}")
    implementation("io.ktor:ktor-serialization-kotlinx-json:${property("ktorVersion")}")
    
    // 日志依赖
    implementation("ch.qos.logback:logback-classic:${property("logbackVersion")}")
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