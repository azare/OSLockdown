/*
*
* Copyright (c) 2009-2014 Forcepoint LLC.
* This file is released under the GPLv3 license.  
* See 'GPLv3_LICENSE.txt' at the root of the source tree for the full license,
* or visit https://www.gnu.org/licenses/gpl.html instead.
*
* OSLockdown Dispatcher
*/

#ifndef SB_DISPATCHER_UTILS_H
#define SB_DISPATCHER_UTILS_H

#include <pthread.h>
#include <iostream>
#include <sstream>
#include <vector>
#include <exception>
#include <syslog.h>
#include <openssl/crypto.h>
#include <unistd.h>
using namespace std;

// This originally was tied to the type of Console generating the request, but we're going to rename it to represent the
// type of Client that is being tasked, Note that the EXACT values are defined in 
// grails/OSLockdown/src/groovy/com/trustedcs/sb/util/ClientType.groovy.  The following enum *MUST* be kept in lockstep.

enum SB_CLIENT_ENUM   {CLIENT_STANDALONE=0, CLIENT_ENTERPRISE, CLIENT_BULK,CLIENT_ZSERIES, CLIENT_AIX};

enum SB_ACTION_ENUM   { SB_SCAN=0, SB_QSCAN, SB_APPLY, SB_UNDO, SB_BASELINE, SB_GROUP_ASSESSMENT,SB_BASELINE_COMPARISON,
                        SB_SCHEDULED_SCAN, SB_SCHEDULED_QSCAN, SB_SCHEDULED_APPLY, SB_SCHEDULED_BASELINE,
		                SB_TASK_COMPLETED, SB_AUTOUPDATE_CLIENT, SB_TASK_LAST_ACTION};
const string SB_ACTION_TEXT[]={ "SCAN", "QSCAN", "APPLY", "UNDO", "BASELINE","GROUP ASSESSMENT", "BASELINE_COMPARISON",
                              "SCHEDULED SCAN", "SCHEDULED QSCAN","SCHEDULED_APPLY", "SCHEDULED_BASELINE",
			                  "TASK COMPLETED","AUTOUPDATE CLIENT", ""};

enum SB_TASK_VERIFY_CODE {SB_TASK_VALID=0, SB_TASK_NOPROFILE, SB_TASK_INVALID, SB_TASK_NEWPROFILE };

string prodTypeToString(SB_CLIENT_ENUM prodEnum);
string getCurrentProcessor();

class SBDispatcher_Except: public exception
{
  private:
    void gen_text(){ ostringstream message ; message << "Code:"<<m_code<<" Reason:"<< m_text; m_fulltext=message.str(); }; 
  public:
    int m_code;
    string m_text;
    string m_fulltext;
    ~SBDispatcher_Except() throw() {};
    const char* what() const throw()  { return m_fulltext.c_str();}
    SBDispatcher_Except() {m_code = 200; m_text="no details"; gen_text();};
    SBDispatcher_Except(int code, string details) { m_code=code; m_text=details; gen_text();};
};


class SB_ACTION
{
  private:
    pthread_t           m_thread;        // which thread is doing the work
    pthread_mutex_t     m_mutex;         // lock mutex for updating this thread
    bool                m_kill_flag;     // should this thread die an early death? (note - no async killing )
  public:
    string              m_action_chars;  // sequence of actions (Q=quick, S=scan, U=undo, A=apply, B=Baseline)
    int                 m_actionIdx; // index of the current scheduledTask subaction
    SB_CLIENT_ENUM        m_prodtype;  
    string		m_baseline_profilepath;   // optional profile path for baseline profiles
    string		m_security_profilepath;   // optional profile path for security profiles
    vector<string>      m_procinfo;               // string for approved processor name for *this* client
    int 		m_loggingLevel;
    string              m_sb_command;    // command that OSLockdown should run
    string    	        m_whofrom;
    string    	        m_action_idx;    // Scan, Apply, etc...
    string    	        m_transid;       // transaction id (generated by requester)
    string              m_replyto;       // URL to reply to (empty if no reply needed)
    string              m_verifyaddr;    // URL to reply to (empty if no reply needed)
    bool                m_from_console;  // from console, or scheduled
    bool                m_forceFlag;     // for AutoUpdate, should the force flag be used?
    SB_ACTION_ENUM        m_type;          // type of command, set in initial handler
    SB_ACTION(string transid="",string replyto="",bool from_console=true);
    ~SB_ACTION();
    void kill();
    void set_thread();
};

class SB_DirEntry
{
  public:
    string m_filename;
    time_t m_timestamp;
    size_t m_filesize;
    SB_DirEntry(string filename,time_t timestamp, size_t filesize) {m_filename=filename;m_timestamp=timestamp;m_filesize=filesize;};
};

class SB_DirList
{
  private:
    string m_dirname;
    string m_suffix;
    string m_kind;
    string m_reason;
    bool m_valid;
    vector<SB_DirEntry> m_files;
    void populate();
  public:
    SB_DirList(string dirname="",string suffix="",string kind="");
    string toXml();
};
struct CRYPTO_dynlock_value
{
  pthread_mutex_t mutex;
};

/* 
  This structure contains *all* options that could be on the commandline *or* as part of the sbdispatcher.properties file

 */
struct DISPATCHER_OPTS
{
  int port;
  bool skip_host;
  bool use_https;
  bool daemonize;
  bool verbose;
  bool integrity_check;
  int loglevel;
  int start_time;
  int end_time;
  int max_log_MB;
  double max_load;
  string shim_name;
  string interface;
  string address;
  string ciphers;
  string commonname;
  int recv_timeout;
  int send_timeout;
  int accept_timeout;
};

extern void read_dispatcher_properties(DISPATCHER_OPTS& opts);
extern void init_disp_opts(DISPATCHER_OPTS& opts);
void Verify_Am_Root();

/* treat all this crypto/lock stuff for SSL with with C linkage...*/
#ifdef __cplusplus
extern "C" 
{
#endif

/* public functions */
void CRYPTO_thread_setup();
void CRYPTO_thread_cleanup();

/* static/private functions */

static void my_lock_core(int mode, CRYPTO_dynlock_value *ptr, const char *file, int line);
static void my_lock(int mode, int n, const char *file, int line);
static long unsigned int my_id();
static void my_dyn_lock(int mode, struct CRYPTO_dynlock_value *ptr, const char *file, int line);
static struct CRYPTO_dynlock_value * my_dyn_create(const char *file, int line);
static struct CRYPTO_dynlock_value *my_lock_create(const char *file, int line);
static void my_dyn_destroy(struct CRYPTO_dynlock_value *ptr, const char *file, int line);
#ifdef __cplusplus
}
#endif

extern char *simple_prompt (const char *prompt, int maxlen, int echo);

extern void SB_make_full_path(const string targetpath);
extern bool log_to_stderr;
extern int SB_Daemonize(void);
extern void search_replace(string &, string&, string&);
extern char *password_cb (const char *prompt);
extern string action_text(SB_ACTION_ENUM);
extern bool insideCoreHours(int hour);
extern string ShowAsTwelveHourClock(int hour);
extern bool isValidClientType(int clientType);

extern void write_log (int level, const char *fmt, ...);
#endif // SB_DISPATCHER_UTILS_H