// 现在使用 kotlin {} 配置块，不再需要导入 KotlinCompile

plugins {
    kotlin("jvm") version "2.2.0" apply false
    kotlin("plugin.serialization") version "2.2.0" apply false
}

allprojects {
    group = "com.llmservice"
    version = "1.0-SNAPSHOT"

    repositories {
        // 阿里云镜像仓库，提升国内下载速度
        maven { url = uri("https://maven.aliyun.com/repository/public/") }
        maven { url = uri("https://maven.aliyun.com/repository/gradle-plugin") }
        maven { url = uri("https://maven.aliyun.com/repository/google") }
        maven { url = uri("https://maven.aliyun.com/repository/jcenter") }
        mavenCentral()
        gradlePluginPortal()
    }
}

subprojects {
    apply(plugin = "org.jetbrains.kotlin.jvm")
    apply(plugin = "org.jetbrains.kotlin.plugin.serialization")
    apply(plugin = "java")

    configure<org.jetbrains.kotlin.gradle.dsl.KotlinJvmProjectExtension> {
        compilerOptions {
            jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_21)
            progressiveMode.set(true)
        }
    }
    
    configure<JavaPluginExtension> {
        toolchain {
            languageVersion.set(JavaLanguageVersion.of(21))
        }
    }
    
    dependencies {
        val implementation by configurations
        val testImplementation by configurations
        
        // Kotlin标准库 - 所有子模块都需要
        implementation("org.jetbrains.kotlin:kotlin-stdlib-jdk8")
        implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:${property("coroutinesVersion")}")
        implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:${property("serializationVersion")}")
        
        // 基础测试依赖
        testImplementation("org.jetbrains.kotlin:kotlin-test")
        testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")
        testImplementation("org.junit.jupiter:junit-jupiter-engine:${property("junitVersion")}")
        testImplementation("io.mockk:mockk:${property("mockkVersion")}")
        testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:${property("coroutinesVersion")}")
    }
    
    tasks.named<Test>("test") {
        useJUnitPlatform()
    }
}