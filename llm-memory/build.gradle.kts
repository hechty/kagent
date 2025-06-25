plugins {
    kotlin("jvm")
    kotlin("plugin.serialization")
}

dependencies {
    // 依赖 llm-dsl-core 模块
    implementation(project(":llm-dsl-core"))
    
    // 图数据库和图算法
    implementation("org.neo4j.driver:neo4j-java-driver:5.15.0")
    implementation("org.jgrapht:jgrapht-core:1.5.2")
    implementation("org.jgrapht:jgrapht-io:1.5.2")
    
    // 机器学习和向量计算
    implementation("org.nd4j:nd4j-native-platform:1.0.0-M2.1")
    implementation("org.deeplearning4j:deeplearning4j-core:1.0.0-M2.1")
    
    // 向量数据库客户端
    implementation("io.qdrant:client:1.7.0")
    
    // 缓存和持久化
    implementation("org.ehcache:ehcache:3.10.8")
    implementation("com.h2database:h2:2.2.224")
    
    // 日志
    implementation("io.github.oshai:kotlin-logging-jvm:5.1.0")
    implementation("ch.qos.logback:logback-classic:${property("logbackVersion")}")
    
    // 测试依赖
    testImplementation("org.jetbrains.kotlin:kotlin-test")
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")
    testImplementation("org.junit.jupiter:junit-jupiter-engine:${property("junitVersion")}")
    testImplementation("io.mockk:mockk:${property("mockkVersion")}")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:${property("coroutinesVersion")}")
    testImplementation("org.testcontainers:testcontainers:1.19.3")
    testImplementation("org.testcontainers:junit-jupiter:1.19.3")
    testImplementation("org.testcontainers:neo4j:1.19.3")
}

tasks.named<Test>("test") {
    useJUnitPlatform()
}