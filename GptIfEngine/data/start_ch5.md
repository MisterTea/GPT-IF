All of the free soda and alcohol on the ship is finally having an effect on your bladder. With June's permission, you make a quick stop at the crew restroom. You open one of the stall doors and inside the bathroom stall lies an elderly man in an officer's uniform. The man is clutching his heart. Blood is streaming from the man's mouth as he struggles for air.

{{ world.ask_to_press_key() }}

You rush over to the man and hold his head upright. As you are about to scream for help, his hand clasps over your mouth, as a feeble plea for privacy:

**Officer Schooner:** Listen, boy... There was a terrorist in the engine room planting a bomb. I caught him in the turbine chamber. I grabbed him from behind and was able to subdue him and put handcuffs, but along the way to the security office he stabbed me with a dart... I think it was fentanyl... Dammit...

You plead with the officer to let you carry him to medical, but he shakes his head.

**Officer Schooner:** I'm the second in command on the Fortuna, and I've worked for this ship my entire adult life. I never thought I would see this ship on the open water again after COVID and years in dry dock. This ship is my life.

The officer is having a harder time speaking. It's clear he only has moments left. As he continues, you say a prayer for the man. You realize that you have never witnessed someone pass away in front of your eyes. All of a sudden, something he says snaps you to attention.

{{ world.ask_to_press_key() }}

**Officer Schooner:** ...and that's why you have to save the ship. If we alert the police, the terrorist will detonate the bomb immediately and the ship will be lost. But, the terrorist doesn't know that you are hearing this story. If you can disable the bomb before the terrorist plans to detonate it, we can save the ship and also get evidence to catch the bastard that did this.

All of the color drains from your face. You can't help but look around the room, expecting someone to run into the restroom from anywhere and explain how this has all been an elaborate prank. The door to the restroom remains closed.

**Officer Schooner:** ...please, for me... Go to the gym. Officers always leave their clothes and ID cards in lockers without locking them. Go to the engine room. The terrorist has dark...

The officer begins convulsing. Spit forming at his mouth starts to resemble foam as he utters his last breath. Officer Schooner is no more.

{{ world.ask_to_press_key() }}

You rush back into the crew hallway, eyes wide as spotlights. You can barely sputter the words "Officer heart attack" before the world begins to go dark and you grow weak at the knees. You collapse to a sitting position.

{% if world.agents["vip_reporter"].friend_points >= 2 %}Nancy Smith rushes to help you up, "Hey! Take deep breaths. Relax..."
{% elif world.agents["ex_convict"].friend_points >= 2 %}Tiny Ed grabs you under your arm and lifts you back up, "Hey, buddy! Everything's going to be ok. We'll get through this."
{% elif world.agents["tour_guide"].friend_points >= 2 %}June gets down to your level and locks her blue eyes on you, "It's ok, everything's going to be just fine."
{% else %}None of the other tour members help you up.
{% endif %} June radios in for medical and security, and they swoop in and file into the restroom. A plump lady with a wide smile and a name tag reading "DR SUE" gives you some quick breathing exercises and then follows the squad into the restroom to evaluate the downed officer. After a few minutes, they emerge carrying a stretcher. On the stretcher, the officer is covered from head to toe in a white cloth. It does not look like the officer is breathing and his face is fully covered.

{{ world.ask_to_press_key() }}

**June Hope:** Ladies and gentleman, given such a traumatic event, I believe the best course of action is to postpone the remainder of the tour. I promise I will conduct a second VIP tour later on in our journey. For now, please take some time to heal and care for yourself.

June walks over to you and puts an arm around your shoulder, then whispers in your ear.

**June Hope (whispering):** I spoke with Captain John, and your tab is on us. We will cover any expenses you incur on this cruise. Please have a drink on us to calm your nerves.

And with that, folks begin to disperse. You make your way back to the atrium, where your cruise started. But, the carefree sense of joy that you had when you first entered the atrium is lost. You have less than twenty four hours to live.

{{ world.ask_to_press_key() }}

{{ world.move_to("atrium") }}
