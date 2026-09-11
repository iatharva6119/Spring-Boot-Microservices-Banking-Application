@echo off
setlocal enabledelayedexpansion

set services=API-Gateway Account-Service Fund-Transfer Sequence-Generator Service-Registry Transaction-Service User-Service
set img_prefix=spring-boot-microservices-banking-application

for %%S in (%services%) do (
    set svc=%%S
    set lc_svc=!svc:A=a!
    set lc_svc=!lc_svc:B=b!
    set lc_svc=!lc_svc:C=c!
    set lc_svc=!lc_svc:D=d!
    set lc_svc=!lc_svc:E=e!
    set lc_svc=!lc_svc:F=f!
    set lc_svc=!lc_svc:G=g!
    set lc_svc=!lc_svc:H=h!
    set lc_svc=!lc_svc:I=i!
    set lc_svc=!lc_svc:J=j!
    set lc_svc=!lc_svc:K=k!
    set lc_svc=!lc_svc:L=l!
    set lc_svc=!lc_svc:M=m!
    set lc_svc=!lc_svc:N=n!
    set lc_svc=!lc_svc:O=o!
    set lc_svc=!lc_svc:P=p!
    set lc_svc=!lc_svc:Q=q!
    set lc_svc=!lc_svc:R=r!
    set lc_svc=!lc_svc:S=s!
    set lc_svc=!lc_svc:T=t!
    set lc_svc=!lc_svc:U=u!
    set lc_svc=!lc_svc:V=v!
    set lc_svc=!lc_svc:W=w!
    set lc_svc=!lc_svc:X=x!
    set lc_svc=!lc_svc:Y=y!
    set lc_svc=!lc_svc:Z=z!

    echo Restoring %%S from docker image %img_prefix%-!lc_svc!...
    mkdir %%S\target 2>nul
    
    REM create temporary container
    docker create --name temp-%%S %img_prefix%-!lc_svc!:latest
    
    REM copy jar
    docker cp temp-%%S:/app/app.jar %%S\target\%%S-restored.jar
    
    REM remove container
    docker rm temp-%%S
)
echo All JARs restored.
