# White-Box Hunt — finding the file-read sink in source

## The grep corpus — the sink-names to hunt

### PHP

```
file_get_contents( readfile( fpassthru( file( fopen( fread( fgets( 
fgetcsv( fscanf( fgetss( highlight_file( show_source( readgzfile( 
gzfile( readline( spl_file_object( SplFileObject( SplTempFileObject( 
parse_ini_file( parse_ini_string( file( include( include_once( 
require( require_once( virtual( file_exists( filesize( filetype( 
fileatime( filectime( filemtime( filegroup( fileowner( fileinode( 
fileperms( is_file( is_dir( is_link( is_readable( is_writable( 
is_executable( is_uploaded_file( is_link( realpath( dirname( basename( 
pathinfo( glob( scandir( opendir( readdir( closedir( dir( 
DirectoryIterator( FilesystemIterator( GlobIterator( 
RecursiveDirectoryIterator( RecursiveIteratorIterator( 
RecursiveTreeIterator( Phar( PharData( PharFileInfo( Phar:: 
md5_file( sha1_file( hash_file( hash_init( hash_update( hash_final( 
getimagesize( exif_read_data( iptcparse( getimagesizefromstring( 
imagecreatefrom* ( imagecreatefromstring( finfo_file( finfo_open( 
mime_content_type( pathinfo( readlink( linkinfo( lstat( stat( 
fstat( clearstatcache( disk_total_space( disk_free_space( 
tempnam( tmpfile( sys_get_temp_dir( 
```

### Python

```
open( file( io.open( codecs.open( numpy.load( numpy.genfromtxt( 
numpy.fromfile( pandas.read_* ( pandas.read_csv( pandas.read_json( 
pandas.read_excel( pandas.read_parquet( pandas.read_pickle( 
pandas.read_sql( pandas.read_xml( pandas.read_html( pandas.read_hdf( 
pandas.read_feather( pandas.read_orc( pandas.read_sas( pandas.read_spss( 
pandas.read_stata( pandas.read_table( pandas.read_clipboard( 
pandas.read_fwf( pandas.read_gbq( pickle.loads( pickle.load( 
cPickle.loads( cPickle.load( yaml.load( yaml.safe_load( 
yaml.full_load( yaml.unsafe_load( yaml.load_all( yaml.scan( 
yaml.parse( json.load( json.loads( json.loads( xml.etree. 
xml.dom. xml.sax. xml.parsers. lxml.etree. lxml.objectify. 
lxml.html. lxml.sax. defusedxml. plistlib.load( plistlib.loads( 
configparser. ini. toml. tomli. tomllib. configobj. dotenv. 
os.path. pathlib. glob. fnmatch. shutil. tarfile. zipfile. 
gzip. bz2. lzma. zlib. zipfile. zipfile.Path( tarfile.open( 
tarfile.TarFile( zipfile.ZipFile( zipfile.is_zipfile( 
tarfile.is_tarfile( gzip.open( bz2.open( lzma.open( 
send_file( send_from_directory( FileResponse( StaticFiles( 
StreamingResponse( FileResponse( render_template( 
jinja2.Template( jinja2.Environment( mako.template. 
mako.lookup. genshi. chameleon. cheetah. tempita. 
bottle.template( bottle.SimpleTemplate( bottle.TEMPLATE_PATH( 
bottle.view( bottle.static_file( pyramid.renderers. 
turbogears. web2py. django.shortcuts.render( 
django.template( django.http.FileResponse( django.http. 
StreamingHttpResponse( django.views.static. 
django.contrib.staticfiles. flask.send_file( flask.send_from_directory( 
flask.send_file( flask.make_response( flask.render_template( 
flask.render_template_string( fastapi.responses.FileResponse( 
fastapi.responses.StreamingResponse( fastapi.responses.PlainTextResponse( 
fastapi.responses.HTMLResponse( fastapi.responses.JSONResponse( 
fastapi.responses.ORJSONResponse( fastapi.responses.UJSONResponse( 
tornado.web.StaticFileHandler( tornado.web.RequestHandler( 
bottle.static_file( bottle.template( bottle.view( 
os.listdir( os.scandir( os.walk( os.path.join( os.path.realpath( 
os.path.abspath( os.path.normpath( os.path.relpath( os.path.commonpath( 
os.path.commonprefix( os.path.dirname( os.path.basename( 
os.path.splitext( os.path.split( os.path.splitdrive( 
os.path.expanduser( os.path.expandvars( os.path.exists( 
os.path.isfile( os.path.isdir( os.path.islink( os.path.ismount( 
os.path.isabs( os.path.getsize( os.path.getatime( os.path.getmtime( 
os.path.getctime( os.path.samefile( os.path.sameopenfile( 
os.path.samestat( os.path.lexists( os.path.supports_unicode_filenames( 
os.path.altsep( os.path.curdir( os.path.pardir( os.path.sep( 
os.path.pathsep( os.path.defpath( os.path.devnull( os.path.extsep( 
os.path.splitdrive( os.path.splitunc( os.path.splittext( 
os.path.splitroot( os.path.splitdir( os.path.splitfile( 
os.path.splitbase( os.path.splitext( os.path.splitunc( 
os.path.splitroot( os.path.splitdir( os.path.splitfile( 
os.path.splitbase( os.path.splitext( 
os.open( os.fdopen( os.popen( os.remove( os.removedirs( 
os.rename( os.renames( os.replace( os.rmdir( os.stat( 
os.lstat( os.fstat( os.fstatat( os.statvfs( os.fstatvfs( 
os.symlink( os.link( os.readlink( os.realpath( os.abspath( 
os.normpath( os.path.normcase( os.path.normpath( os.path.realpath( 
os.chmod( os.chown( os.lchown( os.fchmod( os.fchmodat( 
os.fchown( os.fchownat( os.fchdir( os.fchroot( os.chdir( 
os.fchdir( os.fchown( os.fchownat( os.fchmod( os.fchmodat( 
os.fstat( os.fstatat( os.fstatvfs( os.fsync( os.fdatasync( 
os.fallocate( os.fadvise( os.fcopy( os.fclone( os.fcopyfile( 
os.fcopyat( os.fcopyfileat( os.fdup( os.flock( os.ffcntl( 
os.fgetxattr( os.flistxattr( os.fremovexattr( os.fsetxattr( 
os.fstat( os.fstatat( os.fstatvfs( os.fsync( os.fdatasync( 
os.fallocate( os.fadvise( os.fcopy( os.fclone( os.fcopyfile( 
os.fcopyat( os.fcopyfileat( os.fdup( os.flock( os.ffcntl( 
os.fgetxattr( os.flistxattr( os.fremovexattr( os.fsetxattr( 
```

### Node

```
fs.readFile( fs.readFileSync( fs.createReadStream( 
fs.createWriteStream( fs.readdir( fs.readdirSync( fs.stat( 
fs.statSync( fs.lstat( fs.lstatSync( fs.fstat( fs.fstatSync( 
fs.exists( fs.existsSync( fs.access( fs.accessSync( 
fs.realpath( fs.realpathSync( fs.readlink( fs.readlinkSync( 
fs.mkdir( fs.mkdirSync( fs.rmdir( fs.rmdirSync( fs.unlink( 
fs.unlinkSync( fs.rename( fs.renameSync( fs.copyFile( 
fs.copyFileSync( fs.chmod( fs.chmodSync( fs.chown( 
fs.chownSync( fs.lchmod( fs.lchmodSync( fs.lchown( 
fs.lchownSync( fs.fchmod( fs.fchmodSync( fs.fchown( 
fs.fchownSync( fs.ftruncate( fs.ftruncateSync( fs.fsync( 
fs.fsyncSync( fs.fdatasync( fs.fdatasyncSync( fs.futimes( 
fs.futimesSync( fs.appendFile( fs.appendFileSync( 
fs.writeFile( fs.writeFileSync( fs.write( fs.writeSync( 
fs.writev( fs.writevSync( fs.read( fs.readSync( fs.readv( 
fs.readvSync( fs.close( fs.closeSync( fs.open( fs.openSync( 
fs.openAsBlob( fs.fchmod( fs.fchmodSync( fs.fchown( 
fs.fchownSync( fs.fdatasync( fs.fdatasyncSync( fs.fstat( 
fs.fstatSync( fs.fsync( fs.fsyncSync( fs.ftruncate( 
fs.ftruncateSync( fs.futimes( fs.futimesSync( fs.glob( 
fs.globSync( fs.opendir( fs.opendirSync( fs.promises. 
fs.rm( fs.rmSync( fs.cp( fs.cpSync( fs.watch( 
fs.watchFile( fs.unwatchFile( fs.createReadStream( 
fs.createWriteStream( fs.ReadStream( fs.WriteStream( 
fs.FileReadStream( fs.FileWriteStream( fs.Stats( fs.Dirent( 
fs.Dir( fs.constants( fs.promises. fs.readFile( 
fs.readFileSync( fs.createReadStream( fs.readdir( 
fs.readdirSync( fs.stat( fs.statSync( fs.lstat( 
fs.lstatSync( fs.fstat( fs.fstatSync( fs.exists( 
fs.existsSync( fs.access( fs.accessSync( fs.realpath( 
fs.realpathSync( fs.readlink( fs.readlinkSync( fs.mkdir( 
fs.mkdirSync( fs.rmdir( fs.rmdirSync( fs.unlink( 
fs.unlinkSync( fs.rename( fs.renameSync( fs.copyFile( 
fs.copyFileSync( fs.chmod( fs.chmodSync( fs.chown( 
fs.chownSync( fs.lchmod( fs.lchmodSync( fs.lchown( 
fs.lchownSync( fs.fchmod( fs.fchmodSync( fs.fchown( 
fs.fchownSync( fs.ftruncate( fs.ftruncateSync( fs.fsync( 
fs.fsyncSync( fs.fdatasync( fs.fdatasyncSync( fs.futimes( 
fs.futimesSync( fs.appendFile( fs.appendFileSync( 
fs.writeFile( fs.writeFileSync( fs.write( fs.writeSync( 
fs.writev( fs.writevSync( fs.read( fs.readSync( fs.readv( 
fs.readvSync( fs.close( fs.closeSync( fs.open( fs.openSync( 
fs.rm( fs.rmSync( fs.cp( fs.cpSync( fs.watch( 
fs.watchFile( fs.unwatchFile( fs.createReadStream( 
fs.createWriteStream( 
require( import( process.binding( process.dlopen( 
child_process. spawn( exec( execSync( execFile( execFileSync( 
spawn( spawnSync( fork( execPath( argv( env( pid( ppid( 
platform( arch( version( versions( config( title( 
cwd( chdir( umask( getuid( geteuid( getgid( getegid( 
getgroups( setuid( seteuid( setgid( setegid( setgroups( 
initgroups( kill( abort( exit( exitCode( signalCode( 
stdout( stderr( stdin( argv0( execArgv( execPath( 
execPath( debugPort( inspector( inspector.url( inspector.open( 
inspector.close( inspector.waitForDebugger( inspector.console( 
inspector.Session( inspector.Session.prototype.post( 
inspector.Session.prototype.connect( inspector.Session.prototype.disconnect( 
inspector.Session.prototype.send( inspector.Session.prototype.on( 
inspector.Session.prototype.once( inspector.Session.prototype.off( 
inspector.Session.prototype.removeAllListeners( inspector.Session.prototype.listeners( 
inspector.Session.prototype.listenerCount( inspector.Session.prototype.eventNames( 
inspector.Session.prototype.emit( inspector.Session.prototype.addListener( 
inspector.Session.prototype.prependListener( inspector.Session.prototype.prependOnceListener( 
inspector.Session.prototype.removeListener( inspector.Session.prototype.setMaxListeners( 
inspector.Session.prototype.getMaxListeners( inspector.Session.prototype.rawListeners( 
```

### Java

```
new FileInputStream( Files.readAllBytes( Files.readAllLines( 
Files.readString( Files.lines( Files.newBufferedReader( 
Files.newInputStream( Files.newByteChannel( Files.read( 
Files.write( Files.copy( Files.move( Files.delete( 
Files.deleteIfExists( Files.exists( Files.notExists( 
Files.isReadable( Files.isWritable( Files.isExecutable( 
Files.isRegularFile( Files.isDirectory( Files.isSymbolicLink( 
Files.isSameFile( Files.isHidden( Files.size( Files.getLastModifiedTime( 
Files.setLastModifiedTime( Files.getAttribute( Files.setAttribute( 
Files.readAttributes( Files.list( Files.walk( Files.find( 
Files.probeContentType( Files.getFileStore( Files.newDirectoryStream( 
Files.newDirectoryIterator( Files.createDirectory( Files.createDirectories( 
Files.createFile( Files.createTempDirectory( Files.createTempFile( 
Files.createLink( Files.createSymbolicLink( Files.readSymbolicLink( 
Files.getPosixFilePermissions( Files.setPosixFilePermissions( 
Files.getOwner( Files.setOwner( Files.getFileAttributeView( 
Files.getAcl( Files.setAcl( Files.getAclEntry( Files.newBufferedWriter( 
Files.newBufferedReader( Files.newInputStream( Files.newOutputStream( 
Files.newByteChannel( Files.newSeekableByteChannel( 
Files.newDirectoryStream( Files.createDirectory( Files.createDirectories( 
Files.createFile( Files.createTempDirectory( Files.createTempFile( 
Files.createLink( Files.createSymbolicLink( Files.readSymbolicLink( 
FileReader( BufferedReader( FileInputStream( FileOutputStream( 
FileChannel( FileLock( FileDescriptor( RandomAccessFile( 
File( Path( Paths( Path.of( Path.of( Path.of( 
FileSystems( FileSystem( FileStore( FileAttributeView( 
FileAttribute( BasicFileAttributes( PosixFileAttributes( 
DosFileAttributes( AclFileAttributeView( UserDefinedFileAttributeView( 
FileOwnerAttributeView( FileTime( FileVisitResult( 
FileVisitor( SimpleFileVisitor( WatchService( WatchKey( 
WatchEvent( Watchable( StandardWatchEventKinds( 
getResourceAsStream( getClass().getResourceAsStream( 
getClass().getClassLoader().getResourceAsStream( 
Thread.currentThread().getContextClassLoader().getResourceAsStream( 
ServletContext.getResourceAsStream( ServletContext.getRealPath( 
ServletContext.getResource( ServletContext.getResourcePaths( 
ServletContext.getAttribute( ServletContext.getInitParameter( 
ServletContext.getMimeType( ServletContext.getNamedDispatcher( 
ServletContext.getRequestDispatcher( ServletContext.getServlet( 
ServletContext.getServlets( ServletContext.getServletNames( 
ServletContext.getServletContextName( ServletContext.getMajorVersion( 
ServletContext.getMinorVersion( ServletContext.getEffectiveMajorVersion( 
ServletContext.getEffectiveMinorVersion( ServletContext.getServerInfo( 
ServletContext.getContextPath( ServletContext.getServletRegistration( 
ServletContext.getServletRegistrations( ServletContext.getFilterRegistration( 
ServletContext.getFilterRegistrations( ServletContext.getListenerRegistration( 
ServletContext.getListenerRegistrations( ServletContext.getSessionCookieConfig( 
ServletContext.getSessionTimeout( ServletContext.getSessionTrackingModes( 
ServletContext.setSessionTrackingModes( ServletContext.addListener( 
ServletContext.addFilter( ServletContext.addServlet( 
ServletContext.addJspFile( ServletContext.addJspFile( 
ServletContext.declareRoles( ServletContext.setAttribute( 
ServletContext.removeAttribute( ServletContext.getAttributeNames( 
ServletContext.log( ServletContext.getVirtualServerName( 
ServletContext.getEffectiveMajorVersion( ServletContext.getEffectiveMinorVersion( 
ServletContext.getMajorVersion( ServletContext.getMinorVersion( 
ServletContext.getServerInfo( ServletContext.getContextPath( 
ServletContext.getServletContextName( ServletContext.getServletRegistration( 
ServletContext.getServletRegistrations( ServletContext.getFilterRegistration( 
ServletContext.getFilterRegistrations( ServletContext.getListenerRegistration( 
ServletContext.getListenerRegistrations( ServletContext.getSessionCookieConfig( 
ServletContext.getSessionTimeout( ServletContext.getSessionTrackingModes( 
ServletContext.setSessionTrackingModes( ServletContext.addListener( 
ServletContext.addFilter( ServletContext.addServlet( 
ServletContext.addJspFile( ServletContext.declareRoles( 
ServletContext.setAttribute( ServletContext.removeAttribute( 
ServletContext.getAttributeNames( ServletContext.log( 
ServletContext.getVirtualServerName( 
```

### Ruby

```
File.read( File.readlines( File.foreach( File.open( 
File.binread( File.binwrite( File.write( File.binwrite( 
File.extname( File.basename( File.dirname( File.expand_path( 
File.absolute_path( File.realpath( File.realdirpath( 
File.fnmatch( File.fnmatch?( File.identical?( File.join( 
File.path( File.split( File.truncate( File.umask( 
File.stat( File.lstat( File.fstat( File.atime( 
File.ctime( File.mtime( File.birthtime( File.size( 
File.size?( File.zero?( File.exist?( File.exists?( 
File.file?( File.directory?( File.symlink?( File.readable?( 
File.writable?( File.executable?( File.executable_real?( 
File.readable_real?( File.writable_real?( File.owned?( 
File.grpowned?( File.pipe?( File.socket?( File.blockdev?( 
File.chardev?( File.setuid?( File.setgid?( File.sticky?( 
File.world_readable?( File.world_writable?( File.ftype( 
File.chmod( File.chown( File.lchmod( File.lchown( 
File.link( File.symlink( File.rename( File.delete( 
File.unlink( File.utime( File.lutime( File.mkfifo( 
File.truncate( File.open( File.new( File.foreach( 
File.readlines( File.read( File.binread( File.write( 
File.binwrite( File.extname( File.basename( File.dirname( 
File.expand_path( File.absolute_path( File.realpath( 
File.realdirpath( File.fnmatch( File.fnmatch?( File.identical?( 
File.join( File.path( File.split( File.truncate( 
File.umask( File.stat( File.lstat( File.fstat( 
File.atime( File.ctime( File.mtime( File.birthtime( 
File.size( File.size?( File.zero?( File.exist?( 
File.exists?( File.file?( File.directory?( File.symlink?( 
File.readable?( File.writable?( File.executable?( 
File.executable_real?( File.readable_real?( File.writable_real?( 
File.owned?( File.grpowned?( File.pipe?( File.socket?( 
File.blockdev?( File.chardev?( File.setuid?( File.setgid?( 
File.sticky?( File.world_readable?( File.world_writable?( 
File.ftype( File.chmod( File.chown( File.lchmod( 
File.lchown( File.link( File.symlink( File.rename( 
File.delete( File.unlink( File.utime( File.lutime( 
File.mkfifo( File.truncate( 
IO.read( IO.readlines( IO.foreach( IO.open( 
IO.binread( IO.binwrite( IO.write( IO.sysopen( 
IO.new( IO.popen( IO.select( IO.pipe( IO.copy_stream( 
IO.try_convert( IO.console( IO.readpartial( IO.read_nonblock( 
IO.read( IO.readlines( IO.gets( IO.getc( 
IO.readchar( IO.each( IO.each_line( IO.each_byte( 
IO.each_char( IO.each_codepoint( IO.each_index( IO.each_object( 
IO.each_entry( IO.each_member( IO.each_pair( IO.each_value( 
IO.each_key( IO.each_with_index( IO.each_with_object( 
IO.each_cons( IO.each_slice( IO.each_vmsg( IO.each_prefix( 
IO.each_delim( IO.each_break( IO.each_limit( IO.each_slice( 
IO.each_cons( IO.each_vmsg( IO.each_prefix( IO.each_delim( 
IO.each_break( IO.each_limit( IO.each_slice( IO.each_cons( 
IO.each_vmsg( IO.each_prefix( IO.each_delim( IO.each_break( 
IO.each_limit( IO.each_slice( IO.each_cons( IO.each_vmsg( 
IO.each_prefix( IO.each_delim( IO.each_break( IO.each_limit( 
IO.each_slice( IO.each_cons( IO.each_vmsg( IO.each_prefix( 
IO.each_delim( IO.each_break( IO.each_limit( IO.each_slice( 
IO.each_cons( IO.each_vmsg( IO.each_prefix( IO.each_delim( 
IO.each_break( IO.each_limit( 
```

The hunt-corpus — the sink-names per stack — `grep`-searches in source.

## The "the sink names the param" — the param-sink map

The file-read's PARAM is the `?file=`/`?path=`/`?doc=`/`?template=`/
`?page=`/`?include=`/`?load=`/`?read=`/`?img=`/`?src=`/`?content=`/
`?name=`/`?download=`/`?open=`/`?show=`/`?filename=`/`?filepath=`/
`?resource=`/`?location=`/`?uri=`/`?url=`/`?doc_name=`/`?docname=` —
the sink's INPUT is the param — the param-sink map is the white-box hunt.

## The "the path-prefix reveals the confine" — the confine-check

`$base + $input`/`os.path.join(base, input)`/`path.join(base, input)`/
`File.join(base, input)` — the join-call — the confine-check's exact
expression is the bypass-target — `denied-conditions.md`.

## The "the sink calls the sink" — the call-chain

`download`→`open`/`export`→`send_file`/`view`→`File.read` — the route
→ the sink — the call-chain is the read-path — `find`/`grep` for the
route-name → the sink-call.

## The "the wrapper is in the URL-allowlist" — the allowlist

`allowed_schemes = ['http', 'https']` — the URL-allowlist — a `file://`
still reaches the handler if the allowlist doesn't check scheme —
the allowlist-bypass.

## The "the read is inside a larger flow" — the flow-hunt

`/export` → `read-template` → `render` → `send` — the file-read is
inside a multi-step flow — the flow-hunt follows the param from
route to sink.
