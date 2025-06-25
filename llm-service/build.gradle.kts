plugins {
    kotlin("jvm")
    kotlin("plugin.serialization")
    application
}

dependencies {
    // DSL模块依赖
    implementation(project(":llm-dsl-core"))
    
    // 服务器依赖 - 服务模块特有
    implementation("io.ktor:ktor-server-core:${property("ktorVersion")}")
    implementation("io.ktor:ktor-server-netty:${property("ktorVersion")}")
    implementation("io.ktor:ktor-server-content-negotiation:${property("ktorVersion")}")
    implementation("io.ktor:ktor-serialization-kotlinx-json:${property("ktorVersion")}")
    
    // 日志依赖
    implementation("ch.qos.logback:logback-classic:${property("logbackVersion")}")
    
    // 服务测试依赖
    testImplementation("io.ktor:ktor-server-tests:${property("ktorVersion")}")
}

application {
    mainClass.set("com.llmservice.ApplicationKt")
}