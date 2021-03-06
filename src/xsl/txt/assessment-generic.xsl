<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <!-- 
     =========================================================================
         Copyright (c) 2007-2014 Forcepoint LLC.
         This file is released under the GPLv3 license.  
         See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
	 or visit https://www.gnu.org/licenses/gpl.html instead.
         
         Purpose: Assessment Report XML to TEXT
     =========================================================================
    -->
    <xsl:param name="report.lang">en</xsl:param>
    <xsl:param name="report.title">Assessment Report</xsl:param>
    
    <xsl:include href="common-text.xsl"/>
    <xsl:output method="text" encoding="UTF-8" indent="yes" />
    
    <xsl:template match="/">
        <xsl:text>&#x0A;</xsl:text>
        <xsl:value-of select="translate($report.title, $vLower, $vUpper)"/>
        <xsl:text>&#x0A;Created </xsl:text>
        <xsl:value-of select="/AssessmentReport/report/@created"/>
        <xsl:text> by OS Lockdown v</xsl:text>
        <xsl:value-of select="/AssessmentReport/@sbVersion"/>

        <xsl:text>&#x0A;&#x0A;</xsl:text>
        <xsl:text>Summary:&#x0A;</xsl:text>
        <xsl:text>--------------------------------------------------------------------</xsl:text>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:text>         Created: </xsl:text><xsl:value-of select="/AssessmentReport/report/@created"/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>        Hostname: </xsl:text><xsl:value-of select="/AssessmentReport/report/@hostname"/>
        <xsl:text>&#x0A;</xsl:text>

        <xsl:text>Operating System: </xsl:text>
        <xsl:variable name="distVersion" select="/AssessmentReport/report/@distVersion"/>
        <xsl:variable name="dist" select="/AssessmentReport/report/@dist"/>
        <xsl:choose>
            <xsl:when test="$distVersion = '10' and $dist = 'redhat'">
                <xsl:text>Fedora 10</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="/AssessmentReport/report/@dist"/>
                <xsl:text> </xsl:text>
                <xsl:value-of select="/AssessmentReport/report/@distVersion"/>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text> (</xsl:text>
        <xsl:value-of select="/AssessmentReport/report/@arch"/>
        <xsl:text>) [Kernel </xsl:text>
        <xsl:value-of select="/AssessmentReport/report/@kernel"/>
        <xsl:text>]&#x0A;</xsl:text>

        
        <xsl:text>         Profile: </xsl:text><xsl:value-of select="/AssessmentReport/report/@profile"/>
        <xsl:text>&#x0A;</xsl:text>

        <xsl:variable name="modFail" select="count(/AssessmentReport/modules/module[@results='Fail'])"/>
        <xsl:variable name="modPass" select="count(/AssessmentReport/modules/module[@results='Pass'])"/>
        <xsl:variable name="modOther" select="count(/AssessmentReport/modules/module[@results !='Pass' and @results !='Fail'])"/>
        
        <xsl:text>&#x0A;</xsl:text> 
        <xsl:text>  Modules Failed: </xsl:text><xsl:value-of select="$modFail"/>
        <xsl:text> (</xsl:text>
        <xsl:value-of select="round(($modFail div ($modFail + $modPass)) * 100)"/>
        <xsl:text>%) &#x0A;</xsl:text>
        
        <xsl:text>          Passed: </xsl:text><xsl:value-of select="$modPass"/>
        <xsl:text>&#x0A;</xsl:text>
        <xsl:text>           Other: </xsl:text><xsl:value-of select="$modOther"/>
        <xsl:text>&#x0A;</xsl:text>
        
        <xsl:text>&#x0A;</xsl:text>

        <xsl:if test="count(/AssessmentReport/modules/module[@severity='High']) != 0">
            <xsl:text>&#x0A;High Risk:&#x0A;</xsl:text>
            <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
            <xsl:for-each select="/AssessmentReport/modules/module[@severity='High']">
                <xsl:sort select="@name"/>
                <xsl:variable name="spaces">.............................</xsl:variable>
                <xsl:text>   </xsl:text>
                <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
                <xsl:value-of select="@results"/>
                <xsl:text>&#x0A;</xsl:text>
            </xsl:for-each>
        </xsl:if>
        
        <xsl:if test="count(/AssessmentReport/modules/module[@severity='Medium']) != 0">
            <xsl:text>&#x0A;Medium Risk:&#x0A;</xsl:text>
            <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
            <xsl:for-each select="/AssessmentReport/modules/module[@severity='Medium']">
                <xsl:sort select="@name"/>
                <xsl:variable name="spaces">.............................</xsl:variable>
                <xsl:text>   </xsl:text>
                <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
                <xsl:value-of select="@results"/>
                <xsl:text>&#x0A;</xsl:text>
            </xsl:for-each>
        </xsl:if>
        
        <xsl:if test="count(/AssessmentReport/modules/module[@results='Fail' and @severity='Low']) != 0">
            <xsl:text>&#x0A;Low Risk:&#x0A;</xsl:text>
            <xsl:text>--------------------------------------------------------------------&#x0A;</xsl:text>
            <xsl:for-each select="/AssessmentReport/modules/module[@severity='Low']">
                <xsl:sort select="@name"/>
                <xsl:variable name="spaces">.............................</xsl:variable>
                <xsl:text>   </xsl:text>
                <xsl:value-of select="substring(concat(@name, $spaces, $spaces), 1, 60)"/>
                <xsl:value-of select="@results"/>
                <xsl:text>&#x0A;</xsl:text>
            </xsl:for-each>
        </xsl:if>
        
    </xsl:template>
</xsl:stylesheet>
