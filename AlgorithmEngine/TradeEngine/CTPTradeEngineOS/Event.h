#ifndef __EVENT_H__
#define __EVENT_H__

#include <iostream>
#include <string>

using namespace std;

typedef void (*handler_ptr)(void *);

class Event{
    public:
        Event(int max=20){
            sub_funcs = new handler_ptr[max];
            m_max = max;
            m_len = 0;
        }

		~Event(){
			delete sub_funcs;
		}

        void emit(void *object){
            for(int i=0; i < m_len; i++){
                (*sub_funcs[i])(object);
            }
        }

        int subscribe(handler_ptr func){
            for(int i=0; i < m_len; i++){
                if (sub_funcs[i] == func){
					return 0;
				}
            }

            if(m_len < m_max){
                sub_funcs[m_len++] = func;
				return 0;
            }else{
                return -1;
            }
        }

		int unsubscribe(handler_ptr func){
			int index = -1;
			for(int i=0; i < m_len; i++){
                if (sub_funcs[i] == func){
					index = i;
					break;
				}
            }
            if (index != -1){
        		m_len--;
            	for(int i=index; i < m_len; i++){
            		sub_funcs[i] = sub_funcs[i+1];
            	}
            }
			return 0;
		}
    private:
        int m_len;
        int m_max;
        handler_ptr *sub_funcs ;
};

#endif
