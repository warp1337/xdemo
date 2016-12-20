CMAKE_MINIMUM_REQUIRED(VERSION 2.4)

PROJECT(basic-example)
SET(xdemoprefix "${CMAKE_INSTALL_PREFIX}")
SET(xdemoroot "${CMAKE_INSTALL_PREFIX}/etc/xdemo/systems/${PROJECT_NAME}")
MESSAGE( STATUS "XDEMOROOT: ${xdemoroot}")

FILE(GLOB files "*.sh.in")

SET(xdemofiles)
MESSAGE( STATUS "Processing: " )
FOREACH(file ${files})
	GET_FILENAME_COMPONENT(environment ${file} NAME_WE)
	MESSAGE( STATUS "   ${environment}" )
	LIST(APPEND xdemofiles ${environment})
	CONFIGURE_FILE(${file} "etc/${environment}.sh" @ONLY)
	INSTALL(FILES "${CMAKE_CURRENT_BINARY_DIR}/etc/${environment}.sh" DESTINATION "etc/xdemo/systems/${PROJECT_NAME}")
ENDFOREACH()

INSTALL(DIRECTORY "components" DESTINATION "etc/xdemo/systems/${PROJECT_NAME}")

FILE(GLOB groups "groups/*")
LIST(REMOVE_ITEM groups "*~")
INSTALL(
    FILES ${groups}
	DESTINATION "etc/xdemo/systems/${PROJECT_NAME}/groups"
	PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ OWNER_EXECUTE GROUP_EXECUTE WORLD_EXECUTE
)

FILE(GLOB systems "*.yaml")

LIST(REMOVE_ITEM systems "*~")
INSTALL(
    FILES ${systems}
	DESTINATION "etc/xdemo/systems/${PROJECT_NAME}"
	PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ OWNER_EXECUTE GROUP_EXECUTE WORLD_EXECUTE
)