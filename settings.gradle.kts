rootProject.name = "llm-service-multi-module"

include(
    ":llm-dsl-core",
    ":llm-service"
)

project(":llm-dsl-core").projectDir = file("llm-dsl-core")
project(":llm-service").projectDir = file("llm-service")