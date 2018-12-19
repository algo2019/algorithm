#ifndef THREADQUEUE_H_
#define THREADQUEUE_H_

#include <pthread.h>
#include <iostream>

using std::cout;
using std::endl;
const int QUEUESIZE = 200;

template<class Object>
class ThreadQueue
{
public:
    ThreadQueue();
    ~ThreadQueue();
public:
    bool Enter(Object *obj);
    Object* Out();
    bool IsEmpty();
    bool IsFull();
private:
    int front;   //队列头
    int rear;    //队列尾.
    int size;
    Object *list[QUEUESIZE];
    pthread_mutex_t queueMutex;
};

//------------------------------------------------------
template<class Object>
ThreadQueue<Object>::ThreadQueue()
{
    front = rear = 0;
    size = QUEUESIZE;

    pthread_mutex_lock(&queueMutex);
}
//------------------------------------------------------
template<class Object>
bool ThreadQueue<Object>::Enter(Object* obj)
{
    pthread_mutex_lock(&queueMutex);
    if(IsFull())
    {
        cout << "Queue is full!" << endl;
        pthread_mutex_unlock(&queueMutex);

        return false;
    }
	//入队
    list[rear] = obj;
    rear = (rear + 1) % size;

    pthread_mutex_unlock(&queueMutex);

    return true;
}
//------------------------------------------------------ 出队列
template<class Object>
Object* ThreadQueue<Object>::Out()
{
    Object* temp;
    pthread_mutex_lock(&queueMutex);
    if(IsEmpty())
    {
        cout << "Queue is empty!" << endl;
        pthread_mutex_unlock(&queueMutex);

        return false;
    }
    temp = list[front];
    front = (front + 1) % size;

    pthread_mutex_unlock(&queueMutex);

    return temp;
}
//------------------------------------------------------
template<class Object>
bool ThreadQueue<Object>::IsEmpty()
{
    if(rear == front)
        return true;
    else
        return false;
}
//------------------------------------------------------
template<class Object>
bool ThreadQueue<Object>::IsFull()
{
    if((rear + 1) % size == front)
        return true;
    else
        return false;
}
//------------------------------------------------------
template<class Object>
ThreadQueue<Object>::~ThreadQueue()
{
    delete []list;
}
//------------------------------------------------------


#endif /* THREADQUEUE_H_ */