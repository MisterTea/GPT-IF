The Fortuna embarks on her first voyage after sitting in dry dock through the COVID pandemic. The Fortuna is said to be cursed, but still attracts passengers with its promise of good luck...

%%{{ world.render_image("A cursed but lucky cruise ship.") }}%%

{{< pagebreak >}}

It's a beautiful day in Tampa, and you're excited to be taking a taxi to the cruise terminal. You've been planning this cruise for months, and you can't wait to start your adventure. You step outside of your hotel and hail a taxi. The driver is a friendly man named Juan, and he quickly loads your luggage into the trunk. You give him the address of the cruise terminal, and he takes off. As you ride, you look out the window and see the cityscape passing by. You pass by tall buildings, busy streets, and parks. You can see the Hillsborough River in the distance.

%%{{ world.render_image("It's a beautiful day in Tampa, and you're excited to be taking a taxi to the cruise terminal. You've been planning this cruise for months, and you can't wait to start your adventure. You step outside of your hotel and hail a taxi. The driver is a friendly man named Juan, and he quickly loads your luggage into the trunk. You give him the address of the cruise terminal, and he takes off. As you ride, you look out the window and see the cityscape passing by. You pass by tall buildings, busy streets, and parks. You can see the Hillsborough River in the distance.") }}%%

```
Welcome to Fortuna's Folly!
```

```
When you see text like this throughout the adventure, it's me, your humble programmer.  
```

```
Fortuna's Folly is unlike most other text adventures.  To succeed in this game, you must befriend and enlist the help of many other characters. These characters are played by very sophisticated artificial intelligence that has been given specific instructions.  While you cannot see those instructions directly, you can converse with these characters and learn more about them by using the command: ASK/TELL (character) (message).  
```

```
For example, let's see what happens when we make small talk with the driver:
```

{{< pagebreak >}}

\> ask driver "How long have you been a taxi driver?"

> I have been driving a taxi for 20 years now. I started when I first came to Tampa and I've been doing it ever since. It's a great job, and I love meeting new people and seeing the city from behind the wheel of my cab.

%%{{ world.render_image("Portrait of character with description: " + world.describe_agent(world.agents["taxi_driver"])) }}%%

```
You learned something new about Juan!  Big brain move there, buddy!
```

{{< pagebreak >}}

%%{{ world.look() }}%%

```
Now you try it out!  you can TELL Juan "Hello!" or ASK Juan "Where are you from?".  You can also LOOK to view your surroundings, or LOOK AT THE RIVER.  Otherwise, you can WAIT until your taxi ride is over.
```
