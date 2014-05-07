<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <html>
            <body>
                <h2>Test Report (<xsl:value-of select="TestReport/Summary" />)</h2>
                <h3>Test Summary: <br /></h3>
                <h4>
                  <table border="1">
                    <tr>
                      <th align="left">Suite</th>
                      <th align="left">Summary</th>
                    </tr>
                    <xsl:for-each select="TestReport/TestSuite">
                      <tr>
                        <td>
                          <xsl:value-of select="Name" />
                        </td>
                        <td>
                          <xsl:value-of select="Summary" />
                        </td>
                      </tr>
                    </xsl:for-each>
                  </table>
                  <table border="1">
                    <tr>
                      <th align="left">Repeated Case Name</th>
                      <th align="left">Average Value Statistics</th>
                      <th align="left">Fail Rate</th>
                    </tr>
                    <xsl:for-each select="TestReport/TestSuite/RepeatedTestStatistics">
                      <tr>
                        <td>
                          <xsl:value-of select="Name" />
                        </td>
                        <td>
                          <xsl:choose>
                              <xsl:when test="AverageStatistics">
                              <xsl:for-each select="AverageStatistics">
                                  <xsl:value-of select="text()" />
                                  <br/>                     
                              </xsl:for-each>
                            </xsl:when>
                            <xsl:otherwise>
                                N/A
                            </xsl:otherwise>
                          </xsl:choose>
                        </td>
                        <td>
                          <xsl:value-of select="FailRate" />
                        </td>
                      </tr>
                    </xsl:for-each>
                  </table>
                </h4>
                <br />
                <br />
                <xsl:for-each select="TestReport/TestSuite">
                    <h3>
                        Test Suite: <xsl:value-of select="Name" /> (<xsl:value-of select="Summary" />)
                    </h3>
                    <h4>
                      <table border="1">
                        <tr>
                          <th align="left">Test Number</th>
                          <th align="left">Test Title</th>
                          <th align="left">Test Result</th>
                          <th align="left">Test Comment</th>
                        </tr>
                        <xsl:for-each select="Test">
                          <tr>
                            <td>
                                  <xsl:value-of select="Number" />
                            </td>
                            <td>
                                  <xsl:value-of select="Title" />
                            </td>
                            <xsl:choose>
                                <xsl:when test="Result='FAILED'">
                                    <td style="color:red">
                                        <xsl:value-of select="Result"/>
                                    </td>                                                                                             
                                      <td style="color:red">          
                                          <xsl:for-each select="Comment">
                                              <xsl:value-of select="text()" />
                                              <br />
                                          </xsl:for-each>
                                    </td>
                                </xsl:when>                            
                                <xsl:when test="Result='WARNING'">
                                    <td style="color:brown">
                                        <xsl:value-of select="Result"/>
                                    </td>                                                                                             
                                      <td style="color:brown">          
                                          <xsl:for-each select="Comment">
                                              <xsl:value-of select="text()" />
                                              <br />
                                          </xsl:for-each>
                                    </td>                                                                                     
                                </xsl:when>    
                                <xsl:otherwise>
                                    <td>
                                        <xsl:value-of select="Result"/>
                                    </td>
                                      <td>          
                                          <xsl:for-each select="Comment">
                                              <xsl:value-of select="text()" />
                                              <br />
                                          </xsl:for-each>
                                    </td>
                                </xsl:otherwise>
                            </xsl:choose>
                          </tr>
                        </xsl:for-each>
                      </table>
                    </h4>
                    <br />
                </xsl:for-each>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>