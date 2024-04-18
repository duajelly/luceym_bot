import logging

logging.basicConfig(format='%(asctime)s - %(process)d-%(levelname)s - %(message)s', level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')
logging.info('Loading modules')

from config import bot, dp
import handlers.application as application
import handlers.main as main_router
import handlers.timetable as timetable
import handlers.menu as menu
import handlers.events as events
import handlers.subscribe as subsctibe
import handlers.statement as statement
import handlers.check_statement_soc as check_statement_soc


import admin_handlers.timetable_set as admin_timetable_set
import admin_handlers.do_mailing as admin_do_mailing
import admin_handlers.event_set as admin_event_set
import admin_handlers.statement_processing as admin_statement_close
import admin_handlers.statement_reg as admin_statement_reg
import admin_handlers.unclosed_statements as admin_unclosed_statements
import admin_handlers.unclosed_statements_reg as admin_unclosed_statements_reg
import admin_handlers.application_processing as admin_application_close
import admin_handlers.all_applications as admin_all_applications
import admin_handlers.generate_blanks as admin_generate_blanks
import admin_handlers.menu_add as admin_menu_add 

def main() -> None:
    dp.include_router(application.router)    
    dp.include_router(statement.router)  
    
    dp.include_router(timetable.router)
    dp.include_router(menu.router)
    dp.include_router(events.router)  
    dp.include_router(subsctibe.router)    
    dp.include_router(check_statement_soc.router)

    dp.include_router(admin_application_close.router)
    dp.include_router(admin_all_applications.router)
    dp.include_router(admin_statement_reg.router)
    dp.include_router(admin_unclosed_statements.router)
    dp.include_router(admin_do_mailing.router)
    dp.include_router(admin_event_set.router)
    dp.include_router(admin_statement_close.router)
    dp.include_router(admin_timetable_set.router)  
    dp.include_router(admin_unclosed_statements_reg.router)
    dp.include_router(admin_generate_blanks.router)
    dp.include_router(admin_menu_add.router)

    dp.include_router(main_router.router)
    
    dp.run_polling(bot, skip_updates=False)
    
if __name__ == "__main__":
    main()